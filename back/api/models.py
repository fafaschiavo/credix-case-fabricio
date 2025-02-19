from django.db import models

class Product(models.Model):
    """Represents a product that can be ordered."""
    sku = models.CharField(max_length=8)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product"

    def __str__(self):
        return self.name


class Order(models.Model):
    """Represents a customer order."""
    customer_first_name = models.CharField(max_length=255)
    customer_last_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=255)
    customer_email = models.EmailField()
    credix_order_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order"

    def __str__(self):
        return f"{self.id}"


class OrderItem(models.Model):
    """Represents an item in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.id}"
