import json
import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest, JsonResponse
import requests
from amazon.models import Amazon_Order
from common.utils import amazon_sku_to_sage_sku


from danuema.settings import BASE_DIR
from sage.constants import (
    SAGE_BASE_URL,
    Test_Savantini_Ltd,
    ocp_apim_subscription_key,
    X_Site,
    Savantini_Ltd,
)
from .utils import get_access_token
import logging

logger = logging.getLogger("custom_logger")


# Landing page view
def index(request):
    return render(request, "sage/index.html")


############################ Start SOP Orders
# [GET] all sales orders
def sop_orders(request):
    base_url = "https://api.columbus.sage.com/uk/sage200extra/accounts/v1"
    entity_name = "/sop_orders"

    try:
        # Get the access token and new refresh token
        access_token_info = get_access_token()
        access_token = access_token_info["access_token"]

        headers = {
            "X-Site": "6800e15c-6a18-4a3d-bc22-a09f89ac2d01",
            "X-Company": "33",
            "ocp-apim-subscription-key": "7ac78f2533364ff19d00686a7b8a989d",
            "Authorization": f"Bearer {access_token}",
        }

        # Define request parameters
        params = {
            "$orderby": "date_time_created desc",
            "$filter": "analysis_code_4 ne '' and analysis_code_4 ne 'FBA' and endswith(analysis_code_1,'SAV') eq false and contains(analysis_code_1,'-')",
        }

        # URL endpoint
        url = f"{base_url}{entity_name}"

        # Get response
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes

        # Return JSON response
        return JsonResponse(response.json(), safe=False)

    except Exception as e:
        # Log the error
        logger.error(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# [GET] a single sales order
def sop_order(request, order_id):
    base_url = "https://api.columbus.sage.com/uk/sage200extra/accounts/v1"
    endpoint = f"/sop_orders/{order_id}"

    try:

        # Get the access token and new refresh token
        access_token_info = get_access_token()
        access_token = access_token_info["access_token"]

        headers = {
            "Content-Type": "application/json",
            "X-Site": "6800e15c-6a18-4a3d-bc22-a09f89ac2d01",
            "X-Company": "33",
            "ocp-apim-subscription-key": "7ac78f2533364ff19d00686a7b8a989d",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        response.raise_for_status()  # Raise exception fo non-200 status codes

        # Return the JSON response from the Sage API
        return JsonResponse(response.json(), safe=False)

    except Exception as e:
        # Log the error
        logger.error(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# Request type [POST]
# Create the sage order``
def create_sop_order(request, amazon_data):
    # Endpoint URL
    endpoint = f"{SAGE_BASE_URL}/sop_orders"

    try:
        # Initialize request header
        headers = get_access_token_header(
            X_Site, Test_Savantini_Ltd, ocp_apim_subscription_key
        )

        # Get the path to the data.json file
        # file_path = os.path.join(settings.BASE_DIR, "sage", "data.json")

        # Open the file and read its contents
        # with open(file_path, "r") as file:
        #     amazon_data = json.load(file)

        # Get the payload data
        for amazon_order in amazon_data["payload"]["Orders"]:
            AmazonOrderId = amazon_order["AmazonOrderId"]

            # Check if the order already exists in sage application
            order_exists = order_already_exist(endpoint, headers, AmazonOrderId)
            if order_exists:
                logger.info(
                    f"Order with AmazonOrderId: {AmazonOrderId} already exists. Skipping..."
                )
                continue

            # Prepare Amazon data
            data = prepare_sage_order(headers, amazon_order, reference="4000SAMA")

            # Make the POST request
            response = requests.post(endpoint, headers=headers, json=data)

            # Check if the request was successful
            if response.status_code == 200:
                logger.info(
                    f"Order with AmazonOrderId: {AmazonOrderId} created successfully."
                )

                # Save amazon Orders
                for order_item in amazon_order["OrderItems"]:
                    # Saves amazon order to database
                    save_amazon_order(amazon_order, order_item)

            else:
                error_response = response.json()
                error_message = error_response.get("Message", "Unknown error")
                logger.info(
                    f"POST request failed for order {AmazonOrderId} with status code: {response.status_code}. Error message: {error_message}"
                )

        # Return success message if all orders were processed successfully
        return JsonResponse({"message": "All orders processed successfully."})
    except Exception as e:
        return JsonResponse({"error": f"An error occurred here: {e}"}, status=500)


# Get line items
def line_items(base_url, headers, amazon_order):
    # Get amazon id
    AmazonOrderId = amazon_order["AmazonOrderId"]

    # Set lines as a list to append objects to
    lines = []
    # for amazon_order in amazon_data['payload']['Orders']:
    for order_item in amazon_order["OrderItems"]:

        # Check if 'ShippingPrice' exists before accessing it
        shipping_price = float(order_item.get("ShippingPrice", {}).get("Amount", "0"))

        # Get warehouse id
        FulfillmentChannel = amazon_order["FulfillmentChannel"]
        warehouse_id = get_warehouse_id(FulfillmentChannel)

        code = order_item["SellerSKU"]
        OrderItemId = order_item["OrderItemId"]

        # Get product id
        sage_sku, product_id = get_product_id(base_url, headers, code)

        line_quantity = float(order_item["QuantityOrdered"])

        price = float(order_item["ItemPrice"]["Amount"])

        unit_price = price / line_quantity
        ShippingPrice = float(order_item.get("ShippingPrice", {}).get("Amount", 0))
        PromotionDiscount = float(
            order_item.get("PromotionDiscount", {}).get("Amount", 0)
        )

        # Append the line
        lines.append(
            {
                "line_type": "EnumLineTypeStandard",
                "code": sage_sku,
                "description": order_item["Title"],
                "line_quantity": line_quantity,
                "selling_unit_price": unit_price,
                "analysis_code_1": AmazonOrderId,  # add amazon id to code
                "analysis_code_12": OrderItemId,  # add order item id to code
                "unit_discount_value": 0,
                "product_id": product_id,
                "warehouse_id": warehouse_id,
            }
        )

        # Check Shipping price greate than zero
        if shipping_price > 0:
            lines.append(
                {
                    "line_type": "EnumLineTypeCharge",
                    "code": "Carriage",
                    "description": "Delivery",
                    "line_quantity": 1.0,
                    "selling_unit_price": ShippingPrice
                    - PromotionDiscount,  # Convert to float
                }
            )

    return lines


# Save amazon orders to database
def save_amazon_order(amazon_order, order_item):

    AmazonOrderId = amazon_order["AmazonOrderId"]
    PurchaseDate = amazon_order["PurchaseDate"]
    CountryCode = amazon_order["ShippingAddress"]["CountryCode"]  # Add country code
    seller_sku = order_item["SellerSKU"]

    print("Amazon order", amazon_order)
    print("order_item", order_item)

    # amazon to sage sku tranformation
    sage_sku = amazon_sku_to_sage_sku(seller_sku)
    Amazon_Order.objects.create(
        seller_sku=seller_sku,
        sage_sku=sage_sku,
        amazon_order_id=AmazonOrderId,
        order_item_id=order_item["OrderItemId"],
        quantity_ordered=order_item["QuantityOrdered"],
        purchase_date=PurchaseDate,
        country_code=CountryCode,
        unshipped=amazon_order["OrderStatus"],
    )


# Prepare the sage order
def prepare_sage_order(headers, amazon_order, reference):
    payment_type = "AMA"
    document_created_by = "NES_API"

    AmazonOrderId = amazon_order["AmazonOrderId"]
    EarliestDeliveryDate = amazon_order["EarliestDeliveryDate"]
    FulfillmentChannel = amazon_order["FulfillmentChannel"]
    ShipmentServiceLevelCategory = amazon_order["ShipmentServiceLevelCategory"]
    ShipServiceLevel = amazon_order["ShipServiceLevel"]
    PurchaseDate = amazon_order["PurchaseDate"]

    data = {
        "payment_with_order": True,
        "payment_method_id": payment_method_id(SAGE_BASE_URL, headers, payment_type),
        "customer_id": customer_code_id(SAGE_BASE_URL, headers, reference),
        "customer_document_no": AmazonOrderId,
        "document_created_by": document_created_by,
        "requested_delivery_date": PurchaseDate,
        "promised_delivery_date": EarliestDeliveryDate,
        "order_priority": order_priority(
            FulfillmentChannel, ShipmentServiceLevelCategory
        ),
        "analysis_code_1": AmazonOrderId,
        "analysis_code_2": analysis_code_2(ShipServiceLevel),
        "analysis_code_3": analysis_code_3(amazon_order),
        "analysis_code_4": "",
        "analysis_code_5": "",
        "analysis_code_6": analysis_code_6(amazon_order),
        "analysis_code_7": "P",
        "analysis_code_8": "",
        "analysis_code_9": "",
        "analysis_code_10": "",
        "analysis_code_11": "",
        "analysis_code_12": "",
        "analysis_code_13": "",
        "analysis_code_14": "",
        "analysis_code_15": "",
        "analysis_code_16": PurchaseDate,
        "analysis_code_17": "",
        "analysis_code_18": "",
        "analysis_code_19": "",
        "analysis_code_20": "",
        "delivery_address": get_delivery_address(SAGE_BASE_URL, headers, amazon_order),
        "lines": line_items(SAGE_BASE_URL, headers, amazon_order),
    }

    return data


# Handle duplicate orders in sage
def order_already_exist(end_point, headers, amazon_order_id):
    try:
        # Construct the URL for querying the order by its identifier (AmazonOrderId)
        params = {"$filter": f"customer_document_no eq '{amazon_order_id}'"}

        # Make a GET request to check if the order exists
        response = requests.get(end_point, headers=headers, params=params)

        # Check the response status code
        if response.status_code == 200:
            # Parse the JSON response
            order_data = response.json()

            if isinstance(order_data, list) and len(order_data) == 0:
                # If the response is an empty list, the order does not exist
                return False
            else:
                # If the response is not an empty list, the order exists
                return True
        elif response.status_code == 404:
            # Order does not exist
            return False
        else:
            # Handle other status codes if needed
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        # Handle exceptions gracefully
        print(f"An error occurred: {e}")
        return None


############################ End SOP Orders


################################ Handling tracking functions


# [GET] a single sales order for tracking
# def sop_order_tracking(request, order_id):


def get_sage_order(order_id):
    # order_id = "203-1566897-3013500"
    entity_name = "/sop_orders"
    print(order_id)

    try:
        # Intialize request header
        headers = get_access_token_header(
            X_Site, Savantini_Ltd, ocp_apim_subscription_key
        )

        # Define request parameters
        params = {
            "$filter": f"customer_document_no eq '{order_id}'",
            "$select": "document_no, analysis_code_1, analysis_code_2, analysis_code_4, analysis_code_11",
            "$expand": "lines",
        }

        # URL endpoint
        url = f"{SAGE_BASE_URL}{entity_name}"

        # Get response
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes

        # Return the JSON response from the Sage API
        return JsonResponse(response.json(), safe=False)

    except Exception as e:
        # Log the error
        logger.error(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


def get_access_token_header(X_Site, Sage_Account, ocp_apim_subscription_key):
    access_token_info = get_access_token()
    access_token = access_token_info["access_token"]

    headers = {
        "Content-Type": "application/json",
        "X-Site": X_Site,
        "X-Company": Sage_Account,
        "ocp-apim-subscription-key": ocp_apim_subscription_key,
        "Authorization": f"Bearer {access_token}",
    }

    return headers


################################# End tracking


# Get the paymemt_method_id from the sop_payment_methods api
# https://api.columbus.sage.com/uk/sage200extra/accounts/v1/sop_payment_methods
def payment_method_id(base_url, headers, payment_type):

    # Get the end point
    endpoint = f"/sop_payment_methods"

    # Define request parameters
    params = {"$filter": f"name eq '{payment_type}'", "$select": "id"}

    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        response.raise_for_status()  # Raise exception fo non-200 status codes

        sage_payment_method = response.json()
        payment_method_id = sage_payment_method[0]["id"]
        return payment_method_id

    except Exception as e:
        # Log the error
        logger.error(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get the customer_code_id from the customers api
# https://api.columbus.sage.com/uk/sage200extra/accounts/v1/customers
def customer_code_id(base_url, headers, reference):

    # Get the end point
    endpoint = f"/customers"

    # Define request parameters
    params = {
        # "$orderby": 'date_time_created desc',
        "$filter": f"reference eq '{reference}'",
        "$select": "id",
    }

    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        response.raise_for_status()  # Raise exception fo non-200 status codes
        sage_customers_code = response.json()
        sage_customers_code_id = sage_customers_code[0]["id"]

        return sage_customers_code_id

    except Exception as e:
        # Log the error
        logger.error(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get the order_priority
def order_priority(FulfillmentChannel, ShipmentServiceLevelCategory):

    if (FulfillmentChannel == "MFN") & (ShipmentServiceLevelCategory == "Standard"):
        priority = "E"
    if (FulfillmentChannel == "MFN") & (ShipmentServiceLevelCategory == "Expedited"):
        priority = "A"
    if FulfillmentChannel == "AFN":
        priority = "Z"
    else:
        priority = "E"

    return priority


# Get analysis code 2 [Carrier Name]
def analysis_code_2(ShipServiceLevel):

    if ShipServiceLevel == "UK Next":
        serviceLevel = "DPD"
    if ShipServiceLevel == "GB":
        serviceLevel = "ProShipping"
    else:
        serviceLevel = "DHL DAP"

    return serviceLevel


# Get analysis code 3 [OrderDiscount] may just set it to 0
def analysis_code_3(amazon_order):
    for item in amazon_order["OrderItems"]:
        promotion_discount = item.get("PromotionDiscount", {}).get("Amount")
        return promotion_discount


# Get analysis code 6 [Service Type Code]
def analysis_code_6(amazon_order):

    serviceTypeCode = ""
    CountryCode = amazon_order.get("ShippingAddress", {}).get("CountryCode")
    ShipmentServiceLevelCategory = amazon_order["ShipmentServiceLevelCategory"]

    if (CountryCode == "GB") & (ShipmentServiceLevelCategory == "Standard"):
        serviceTypeCode = "TPS"
    elif (CountryCode == "GB") & (ShipmentServiceLevelCategory == "Expedited"):
        serviceTypeCode = "TPN"
    elif (CountryCode != "GB") & (ShipmentServiceLevelCategory == "Standard"):
        serviceTypeCode = "H"
    elif (CountryCode != "GB") & (ShipmentServiceLevelCategory == "Expedited"):
        serviceTypeCode = "P"

    return serviceTypeCode


# Get delivery_address
def get_delivery_address(base_url, headers, amazon_order):

    delivery_address = {}

    amazon_shipping_address = amazon_order["ShippingAddress"]

    delivery_address["contact"] = amazon_shipping_address.get("Name", "")
    delivery_address["postal_name"] = amazon_shipping_address.get("Name", "")
    delivery_address["country"] = amazon_shipping_address.get("CountryCode", "")
    delivery_address["telephone_number"] = amazon_shipping_address.get("Phone", "")
    delivery_address["fax_number"] = amazon_shipping_address.get("Phone", "")
    delivery_address["email_address"] = amazon_order.get("BuyerInfo", {}).get(
        "BuyerEmail", ""
    )

    delivery_address["tax_number"] = ""
    delivery_address["tax_code_id"] = tax_code_id(base_url, headers, amazon_order)
    delivery_address["country_code_id"] = country_code_id(
        base_url, headers, amazon_order
    )

    delivery_address["address_1"] = amazon_shipping_address.get("AddressLine1", "")
    delivery_address["address_2"] = amazon_shipping_address.get("AddressLine2", "")
    delivery_address["address_3"] = amazon_shipping_address.get("AddressLine3", "")
    delivery_address["address_4"] = amazon_shipping_address.get("AddressLine4", "")
    delivery_address["city"] = amazon_shipping_address.get("City", "")
    delivery_address["county"] = amazon_shipping_address.get("County", "")
    delivery_address["postcode"] = amazon_shipping_address.get("PostalCode", "")

    return delivery_address


def tax_code_id(base_url, headers, amazon_order):

    # Get the end point
    endpoint = f"/tax_codes"

    CountryCode = amazon_order.get("ShippingAddress", {}).get("CountryCode", "")

    # Define request parameters
    params = {
        "$filter": f"contains(name, '{CountryCode} ')",  # The space in '{CountryCode} ' is to filter the correct taxcode
        "$select": "id",
    }

    response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
    response.raise_for_status()  # Raise exception fo non-200 status codes

    # get the tax code response
    sage_tax_code = response.json()

    # Get payment id and set the tax_code to default to 2 because GB is not defined in CountryCode
    sage_tax_code_id = 2  # default tax code

    if CountryCode == "GB":
        sage_tax_code_id = 2
        return sage_tax_code_id
    elif len(sage_tax_code) > 0:
        sage_tax_code_id = sage_tax_code[0]["id"]
        return sage_tax_code_id
    else:
        return sage_tax_code_id


def country_code_id(base_url, headers, amazon_order):

    # Get the end point
    endpoint = f"/country_codes"

    CountryCode = amazon_order.get("ShippingAddress", {}).get("CountryCode", "")

    # Define request parameters
    params = {
        "$filter": f"code eq '{CountryCode}'",
        "$select": "id",
    }

    response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
    response.raise_for_status()  # Raise exception fo non-200 status codes

    # get the tax code response
    sage_country_code = response.json()

    # Get payment id and set the tax_code to default to 2 because GB is not defined in CountryCode

    sage_country_code_id = sage_country_code[0]["id"]
    return sage_country_code_id


# Get product Id
def get_product_id(base_url, headers, code):
    try:
        # transform sku
        sage_sku = amazon_sku_to_sage_sku(code)
        # Define endpoint and request parameters
        endpoint = "/products"
        params = {"$filter": f"code eq '{sage_sku}'", "$select": "id"}

        # Send request to retrieve product id
        product_response = requests.get(
            f"{base_url}{endpoint}", headers=headers, params=params
        )
        product_response.raise_for_status()  # Raise error for bad response status

        # Parse response JSON
        sage_product_response = product_response.json()

        # Check if response contains any products
        if sage_product_response:
            # Extract product id from the first product (assuming it's unique)
            product_id = sage_product_response[0]["id"]
            return sage_sku, product_id
        else:
            # If no product found with the given code
            raise ValueError(f"No product found with code '{code}'")

    except requests.RequestException as e:
        # Handle request errors
        print(f"Request error: {e}")
        return None
    except (ValueError, KeyError) as e:
        # Handle other errors related to product retrieval
        print(f"Error retrieving product id: {e}")
        return None


# Get warehouse Id
def get_warehouse_id(FulfillmentChannel):

    Savantini_House_id = 110294514
    FBA_Warehouse_id = 20992

    if FulfillmentChannel == "MFN":
        return Savantini_House_id

    elif FulfillmentChannel == "AFN":
        return FBA_Warehouse_id
    else:
        return Savantini_House_id


###########################################################################################################################
# Client credentials
CLIENT_ID = "XqUEiGFlwYG3iGxlseFfgVWQHM14tjDR"
CLIENT_SECRET = "9tAPWs0Z1JVrYRGSYVZsAaCh2PAkouj5ZnU8x4MiAQyolRwmgcH2kl-ew5IiV_9F"
REDIRECT_URI = "https://sage200nativeapi-nesmailorder.msappproxy.net/Sage200NativeAPI/"
SCOPES = "openid profile email offline_access"


def initiate_auth(request):
    # Redirect the user to Sage ID for authorization
    redirect_url = "https://id.sage.com/authorize"
    client_id = CLIENT_ID
    redirect_uri = REDIRECT_URI
    scopes = "openid profile email offline_access"
    # state = "<your_state_value>"
    authorization_url = f"{redirect_url}?audience=s200ukipd/sage200&client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"

    return redirect(authorization_url)


def handle_callback(request):
    # Handle the callback from Sage and exchange the authorization code for an access token
    # code = request.GET.get('code')
    code = "r3i6cgsM_TLi7kJeOp-7F2LcqIgGHQ1sOUEUQ43pOty9E"
    if not code:
        return HttpResponseBadRequest("Authorization code not found.")

    token_url = "https://id.sage.com/oauth/token"
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    redirect_uri = REDIRECT_URI
    grant_type = "authorization_code"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "grant_type": grant_type,
    }

    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()

    # Store the access token in session
    request.session["Sage_access_token"] = response_data.get("access_token")

    return render(request, "authenticated.html", {"data": response_data})


def authenticated_view(request):
    access_token = request.session.get("Sage_access_token")

    if not access_token:
        return HttpResponseBadRequest("Access token not found.")

    # Use the access token to make authenticated requests to the Sage API
    # Your code for making authenticated requests goes here

    return render(request, "authenticated.html", {"data": access_token})
    # return render(request, 'authenticated.html', {'data': response_data})


#
