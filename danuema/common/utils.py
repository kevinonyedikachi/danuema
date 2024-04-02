from amazon.models import Sage_SKU
from django.db.models import Q

# create function to transform amazon sku to sage
def amazon_sku_to_sage_sku(amazon_sku):
    try:
        # Lookup the Amazon SKU in the Sage_SKU database
        sage_sku_objs = Sage_SKU.objects.filter(Q(amazon_sku=amazon_sku) | Q(amazon_sku=amazon_sku + '*'))
        if sage_sku_objs.exists():
            # If multiple objects found, choose one arbitrarily or based on your criteria
            sage_sku_obj = sage_sku_objs.first()
            sage_sku = sage_sku_obj.sage_sku
        else:
            # If not found, use the Amazon SKU itself
            sage_sku = amazon_sku
    except Sage_SKU.DoesNotExist:
        # If Sage_SKU object doesn't exist, use the Amazon SKU itself
        sage_sku = amazon_sku

    return sage_sku