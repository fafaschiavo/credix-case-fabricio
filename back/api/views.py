import os
from django.http import JsonResponse
import requests
import json
from datetime import datetime, timedelta
from .models import *

# ------------------------------------------------------------------------------
# External API Helper Functions
# ------------------------------------------------------------------------------

def get_buyer(cnpj):
    """
    Retrieves buyer information from the Credix API based on the provided CNPJ.
    
    Args:
        cnpj (str): The Brazilian tax identifier for the buyer.
    
    Returns:
        dict: JSON response from the API containing buyer details.
    """
    url = "https://api.pre.credix.finance/v1/buyers/" + cnpj
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CREDIPAY-API-KEY': os.getenv('CREDIX_API_KEY')
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()

def post_order(data):
    """
    Submits an order to the Credix API.
    
    Args:
        data (dict): The order data payload to be sent to the API.
    
    Returns:
        dict: JSON response from the API after attempting to create the order.
    """
    url = "https://api.pre.credix.finance/v1/orders"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CREDIPAY-API-KEY': os.getenv('CREDIX_API_KEY')
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()

# ------------------------------------------------------------------------------
# API View Functions
# ------------------------------------------------------------------------------

def get_buyer_by_cnpj(request, cnpj):
    """
    View to retrieve buyer information by CNPJ.
    
    Args:
        request (HttpRequest): The HTTP request object.
        cnpj (str): The buyer's CNPJ.
    
    Returns:
        JsonResponse: Contains the buyer data with a success status.
    """
    buyer = get_buyer(cnpj)
    return JsonResponse({
        "status": "success",
        "buyer": buyer
    })

def evaluate_order(data, attach_products=False):
    """
    Evaluates the order details based on incoming data. It performs multiple checks:
      - Retrieves buyer info via external API.
      - Validates the buyer's approval status.
      - Retrieves product details from the database.
      - Calculates order subtotal and taxes.
      - Checks if the buyer has sufficient credit.
      - Determines available payment terms based on seller configuration.
    
    Args:
        data (str): A JSON-formatted string containing order data.
        attach_products (bool): If True, include detailed product info in the result.
    
    Returns:
        dict: Result with status, available terms, order calculations, and optionally product details.
    """
    # Parse the incoming JSON data
    data = json.loads(data)
    
    # Retrieve buyer info using the provided CNPJ
    buyer = get_buyer(data['cnpj'])
    
    # Check if the buyer is approved based on the API response status code
    if 'statusCode' in buyer and buyer['statusCode'] != 200:
        return {
            "status": "error",
            "message": "Buyer not approved"
        }

    products = []
    order_subtotal = 0
    # Process each product item in the order
    for product_item in data['cart']:
        product_sku = product_item['sku']
        try:
            # Fetch the product from the local database using SKU
            product = Product.objects.get(sku=product_sku)
            products.append({
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "quantity": product_item['quantity']
            })
        except Product.DoesNotExist:
            # Return an error if the product isn't found
            return {
                "status": "error",
                "message": "Product not found"
            }
        
        # Add the product cost to the order subtotal
        order_subtotal += product.price * product_item['quantity']
    
    # Ensure the subtotal is a float
    order_subtotal = float(order_subtotal)

    # Calculate order taxes (hardcoded as 10% of the subtotal)
    order_taxes = order_subtotal * 0.1
    order_total_with_tax = order_subtotal + order_taxes

    # Check buyer's available credit (provided in cents) against order total (converted to cents)
    available_credit = buyer['availableCreditLimitAmountCents']
    if available_credit < order_total_with_tax * 100:
        return {
            "status": "error",
            "message": "Insufficient credit"
        }
    
    # Retrieve seller configuration from the buyer data
    sellers = buyer['sellerConfigs']
    # Filter to find the seller that matches the configured SELLER_CNPJ
    seller = [seller for seller in sellers if seller['taxId'] == os.getenv('SELLER_CNPJ')]
    if len(seller) > 0:
        seller = seller[0]
    else:
        return {
            "status": "error",
            "message": "Seller doesn't have terms for this buyer"
        }

    # Determine available payment terms based on the seller's maximum allowed term
    maxPaymentTermDays = seller['maxPaymentTermDays']
    available_terms = [maxPaymentTermDays]
    if maxPaymentTermDays >= 7:
        available_terms.append(7)
    if maxPaymentTermDays >= 14:
        available_terms.append(14)
    if maxPaymentTermDays >= 30:
        available_terms.append(30)

    # Remove duplicate terms and sort them in ascending order
    available_terms = list(set(available_terms))
    available_terms.sort()

    result = {
        "status": "success",
        "terms": available_terms,
        "order_taxes": order_taxes,
        "order_subtotal": order_subtotal,
    }
    # Optionally attach product details to the result
    if attach_products:
        result['products'] = products

    return result

def get_terms(request):
    """
    Endpoint to evaluate an order and return available payment terms and order calculations.
    
    Returns:
        JsonResponse: Contains the evaluation result, or an error if evaluation fails.
    """
    result = evaluate_order(request.body)
    if result['status'] == "error":
        return JsonResponse(result, status=400)
    else:
        return JsonResponse(result)

def order_create(request):
    """
    Endpoint to create an order. It:
      - Evaluates the order data.
      - Validates the selected payment term.
      - Calculates maturity date for installments.
      - Sends the order to the Credix API.
      - Creates order records in the local database.
    
    Returns:
        JsonResponse: Success or error status along with relevant order identifiers.
    """
    # Evaluate order details and attach product info
    result = evaluate_order(request.body, attach_products=True)
    
    # If order evaluation fails, return error response
    if result['status'] == "error":
        return JsonResponse(result, status=400)

    # Parse the request body to extract form data
    data = json.loads(request.body)
    # Ensure that a payment term has been provided
    if 'term' not in data:
        return JsonResponse({
            "status": "error",
            "message": "No term selected"
        }, status=400)
    
    # Validate that the selected term is available
    if data['term'] not in result['terms']:
        return JsonResponse({
            "status": "error",
            "message": "Term not available"
        }, status=400)

    # Get current UTC time for installment maturity calculation
    now = datetime.now()
    # Add the selected term (in days) to determine maturity date
    future_date = now + timedelta(days=data['term'])
    formatted_date = future_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Build the order payload to be sent to the Credix API
    order_data = {
        'subtotalAmountCents': int(result['order_subtotal'] * 100),
        'taxAmountCents': int(result['order_taxes'] * 100),
        'shippingCostCents': 0,
        'installments': [{
            'maturityDate': formatted_date,
            'faceValueCents': int((result['order_subtotal'] + result['order_taxes']) * 100),
        }],
        'buyerTaxId': data['cnpj'],
        'sellerTaxId': os.getenv('SELLER_CNPJ'),
        'items': [{
            'productId': product['sku'],
            'productName': product['name'],
            'quantity': product['quantity'],
            'unitPriceCents': int(product['price'] * 100),
        } for product in result['products']],
        'contactInformation': {
            'email': data['email'],
            'phone': data['phone'],
            'name': data['firstName'],
            'lastName': data['lastName'],
        }
    }

    # Submit the order to the external Credix API
    response = post_order(order_data)

    # If the API returns an error, respond with an error status
    if 'statusCode' in response and response['statusCode'] > 299:
        return JsonResponse({
            "status": "error",
            "message": "Order not created"
        }, status=400)

    # Extract the order ID from the API response
    credix_order_id = response['id']

    # Create a new order record in the local database
    order = Order.objects.create(
        customer_first_name=data['firstName'],
        customer_last_name=data['lastName'],
        customer_phone=data['phone'],
        customer_email=data['email'],
        credix_order_id=credix_order_id
    )
    order.save()

    # Create order item records for each product in the order
    for product in result['products']:
        product_db = Product.objects.get(sku=product['sku'])
        order_item = OrderItem.objects.create(
            order=order,
            product=product_db,
            quantity=product['quantity']
        )
        order_item.save()

    # Return success response with the Credix order ID
    return JsonResponse({
        "status": "success",
        "credix_order_id": credix_order_id,
    })

def index(request):
    """
    A simple view that returns a welcome message for the API.
    
    Returns:
        JsonResponse: A JSON object containing a welcome message.
    """
    return JsonResponse({"message": "Welcome to the Credix case API!"})
