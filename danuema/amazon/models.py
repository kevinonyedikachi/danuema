from django.db import models

# Create your models here.


# Create the Amazon Orders model
class Amazon_Order(models.Model):
    UN_SHIPPED = "Unshipped"
    SHIPPED = "Shipped"

    STATUS_CHOICES = [
        (UN_SHIPPED, "Unshipped"),
        (SHIPPED, "Shipped"),
    ]

    seller_sku = models.CharField(max_length=100)
    sage_sku = models.CharField(max_length=100)
    amazon_order_id = models.CharField(max_length=100)
    order_item_id = models.CharField(max_length=100)
    quantity_ordered = models.IntegerField()
    purchase_date = models.DateTimeField()
    country_code = models.CharField(max_length=100)
    unshipped = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Order {self.amazon_order_id}: {self.unshipped} {self.purchase_date.strftime('%Y-%m-%d')}"


# Sage to Amazon SKU transformation
class Sage_SKU(models.Model):
    sage_sku = models.CharField(max_length=100)
    amazon_sku = models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Shop Name: {self.shop_name} SAGE SKU: {self.sage_sku}, AMAZON SKU: {self.amazon_sku}"
