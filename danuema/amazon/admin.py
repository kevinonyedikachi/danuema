from django.contrib import admin

from amazon.models import Amazon_Order, Sage_SKU

# Register your models here.
admin.site.register(Amazon_Order)
admin.site.register(Sage_SKU)