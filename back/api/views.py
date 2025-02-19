import os
from django.http import JsonResponse
import requests
import json
from datetime import datetime, timedelta
from .models import *

def get_buyer(cnpj):
    url = "https://api.pre.credix.finance/v1/buyers/" + cnpj
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CREDIPAY-API-KEY': os.getenv('CREDIX_API_KEY')
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()

def post_order(data):
    url = "https://api.pre.credix.finance/v1/orders"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CREDIPAY-API-KEY': os.getenv('CREDIX_API_KEY')
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()

def get_buyer_by_cnpj(request, cnpj):
    buyer = get_buyer(cnpj)
    return JsonResponse({
        "status": "success",
        "buyer": buyer
    })

def evaluate_order(data, attach_products=False):
    # Retrieve the form data
    data = json.loads(data)
    buyer = get_buyer(data['cnpj'])
    
    if 'statusCode' in buyer and buyer['statusCode'] != 200:
        return {
            "status": "error",
            "message": "Buyer not approved"
        }

    products = []
    order_subtotal = 0
    for product_item in data['cart']:
        product_sku = product_item['sku']
        # Retrieve the product from the database
        try:
            product = Product.objects.get(sku=product_sku)
            products.append({
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "quantity": product_item['quantity']
            })
        except Product.DoesNotExist:
            # If the product doesn't exist, return an error
            return {
                "status": "error",
                "message": "Product not found"
            }
        
        # Calculate the total amount of the order
        order_subtotal += product.price * product_item['quantity']
    
    order_subtotal=float(order_subtotal)

    # Assuming a hardcoded 10% tax rate
    order_taxes = order_subtotal * 0.1
    order_total_with_tax = order_subtotal + order_taxes

    # Now verify the total amount of credit available for the buyer
    available_credit = buyer['availableCreditLimitAmountCents']
    if available_credit < order_total_with_tax*100:
        return {
            "status": "error",
            "message": "Insufficient credit"
        }
    
    # Now verify the terms available for the buyer
    sellers = buyer['sellerConfigs']

    seller = [seller for seller in sellers if seller['taxId'] == os.getenv('SELLER_CNPJ')]
    if len(seller) > 0:
        seller = seller[0]
    else:
        # If the seller doesn't have terms for the buyer, return an error
        return {
            "status": "error",
            "message": "Seller doesn't have terms for this buyer"
        }

    maxPaymentTermDays = seller['maxPaymentTermDays']

    # The default term is the maximum term
    available_terms = [maxPaymentTermDays]
    # Now that we have the seller, we can check the terms
    if maxPaymentTermDays >= 7:
        available_terms.append(7)

    if maxPaymentTermDays >= 14:
        available_terms.append(14)
    
    if maxPaymentTermDays >= 30:
        available_terms.append(30)

    # Now remove duplicates and sort the terms
    available_terms = list(set(available_terms))
    available_terms.sort()

    result = {
        "status": "success",
        "terms": available_terms,
        "order_taxes": order_taxes,
        "order_subtotal": order_subtotal,
    }
    if attach_products:
        result['products'] = products

    return result


def get_terms(request):
    result = evaluate_order(request.body)
    if result['status'] == "error":
        return JsonResponse(result, status=400)
    else:
        return JsonResponse(result)

def order_create(request):
    result = evaluate_order(request.body, attach_products=True)
    
    # Evaluate the order again to avoid tampering
    if result['status'] == "error":
        return JsonResponse(result, status=400)

    # Check if the term is set and the desired term is available
    data = json.loads(request.body)
    if 'term' not in data:
        return JsonResponse({
            "status": "error",
            "message": "No term selected"
        }, status=400)
    
    if data['term'] not in result['terms']:
        return JsonResponse({
            "status": "error",
            "message": "Term not available"
        }, status=400)

    # Get current UTC time
    now = datetime.now()

    # Add the number days for the term and convert to string
    future_date = now + timedelta(days=data['term'])
    formatted_date = future_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Finally, create the order
    order_data = {
        'subtotalAmountCents': int(result['order_subtotal']*100),
        'taxAmountCents': int(result['order_taxes']*100),
        'shippingCostCents': 0,
        'installments': [{
            'maturityDate': formatted_date,
            'faceValueCents': int((result['order_subtotal']+result['order_taxes'])*100),
        }],
        'buyerTaxId': data['cnpj'],
        'sellerTaxId': os.getenv('SELLER_CNPJ'),
        'items': [{
            'productId': product['sku'],
            'productName': product['name'],
            'quantity': product['quantity'],
            'unitPriceCents': int(product['price']*100),
        } for product in result['products']],
        'contactInformation': {
            'email': data['email'],
            'phone': data['phone'],
            'name': data['firstName'],
            'lastName': data['lastName'],
        }
    }

    # Send the order to the Credix API
    response = post_order(order_data)

    # Check if the order was created successfully
    if 'statusCode' in response and response['statusCode'] > 299:
        return JsonResponse({
            "status": "error",
            "message": "Order not created"
        }, status=400)

    credix_order_id = response['id']

    # Now create the order and order items in our database
    order = Order.objects.create(
        customer_first_name=data['firstName'],
        customer_last_name=data['lastName'],
        customer_phone=data['phone'],
        customer_email=data['email'],
        credix_order_id=credix_order_id
    )
    order.save()

    for product in result['products']:
        product_db = Product.objects.get(sku=product['sku'])
        order_item = OrderItem.objects.create(
            order=order,
            product=product_db,
            quantity=product['quantity']
        )
        order_item.save()

    return JsonResponse({
        "status": "success",
        "credix_order_id": credix_order_id,
    })

def index(request):
    return JsonResponse({"message": "Welcome to the Credix case API!"})