# amazon/utils.py

# Integrate the Amazon API logic into your Django app

import requests
import datetime
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# Get the access token
def get_access_token():
    try:
        token_response = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": os.environ.get("NESAMAZON_REFRESH_TOKEN"),
                "client_id": os.environ.get("NESAMAZON_CLIENT_ID"),
                "client_secret": os.environ.get("NESAMAZON_CLIENT_SECRET"),
            },
        )
        access_token = token_response.json().get("access_token")
        return access_token
    except Exception as e:
        print(f"An error occured while getting access_token: {str(e)}")

    # Get restricted token


def get_restricted_token(access_token, endpoint):
    try:
        restricted_token_response = requests.post(
            f"{endpoint}/tokens/2021-03-01/restrictedDataToken",
            headers={"x-amz-access-token": access_token},
            json={
                "restrictedResources": [
                    {
                        "method": "GET",
                        "path": "/orders/v0/orders",
                        "dataElements": ["buyerInfo", "shippingAddress"],
                    },
                    {"method": "GET", "path": "/orders/v0/orders/{orderId}"},
                    {"method": "GET", "path": "/orders/v0/orders/{orderId}/buyerInfo"},
                    {"method": "GET", "path": "/orders/v0/orders/{orderId}/address"},
                ]
            },
        )
        restricted_token_data = restricted_token_response.json()
        restricted_token = restricted_token_data.get("restrictedDataToken")
        print("Successfully Requested Restricted Data Token")
        return restricted_token
    except Exception as e:
        print(f"An error occurred while getting restricted token: {str(e)}")


def get_json_response(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        raise


def retrieve_orders(endpoint, market_id, restricted_data_token):
    """
    Retrieve orders from the specified endpoint using the provided parameters.

    Args:
    - endpoint: The endpoint URL to retrieve orders from.
    - market_id: The marketplace ID.
    - restricted_data_token: The access token for restricted data.

    Returns:
    - orders_data: The retrieved orders data.
    """
    # Define request parameters
    request_params = {
        "CreatedAfter": (datetime.datetime.now() - datetime.timedelta(days=3)).date(),
        "MarketplaceIds": market_id,
        "OrderStatuses": "Unshipped",
        "FulfillmentChannels": "MFN",
    }

    # Make a request to retrieve orders
    orders_url = (
        endpoint + "/orders/v0/orders" + "?" + urllib.parse.urlencode(request_params)
    )

    try:
        orders_response = requests.get(
            orders_url, headers={"x-amz-access-token": restricted_data_token}
        )

        # Check the response status
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            return orders_data
        else:
            return None

    except requests.RequestException as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


### Start Get amazon orders apis


# GET /orders/v0/orders
# Operation: getOrders
def getOrders(
    Endpoint,
    MarketplaceIds,
    Restricted_data_token,
    CreatedAfter=(datetime.datetime.now() - datetime.timedelta(days=3)).date(),
    FulfillmentChannels=None,
    OrderStatuses=None,
):

    # Set the url enpoint
    url = f"{Endpoint}/orders/v0/orders"

    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "x-amz-access-token": Restricted_data_token,
    }

    # Set the parameters
    params = {
        "MarketplaceIds": MarketplaceIds,
        "CreatedAfter": CreatedAfter,
        "FulfillmentChannels": FulfillmentChannels,
        "OrderStatuses": OrderStatuses,
    }

    # Handle response
    try:
        # Get response
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes

        # return json reponse
        return response.json()
    except requests.RequestException as e:
        # Log the error for debugging purposes
        print(f"Request Exception: {e}")
        raise  # Re-raise the exception to be handled in the Django view
    except Exception as e:
        # Log the error for debugging purpose
        print(f"Error occurred: {e}")
        raise  # Re-raise the exception to be handles in the Django view


# GET /orders/v0/orders/{orderId}
# Operation: getOrder
def getOrder(Endpoint, Restricted_data_token, orderId):
    # Set the url enpoint
    url = f"{Endpoint}/orders/v0/orders/{orderId}"

    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "x-amz-access-token": Restricted_data_token,
    }

    # Handle response
    return get_json_response(url, headers)


# GET /orders/v0/orders/{orderId}/buyerInfo
# Operation: getOrderBuyerInfo
def getOrderBuyerInfo(Endpoint, Restricted_data_token, orderId):
    # Set the url enpoint
    url = f"{Endpoint}/orders/v0/orders/{orderId}/buyerInfo"
    print("this url buyerinfo = ", url)
    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "x-amz-access-token": Restricted_data_token,
    }

    # Handle response
    return get_json_response(url, headers)


# GET /orders/v0/orders/{orderId}/address
# Operation: getOrderAddress
def getOrderAddress(Endpoint, Restricted_data_token, orderId):
    # Set the url enpoint
    url = f"{Endpoint}/orders/v0/orders/{orderId}/address"
    print("this url = ", url)
    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "x-amz-access-token": Restricted_data_token,
    }

    # Handle response
    return get_json_response(url, headers)


# GET /orders/v0/orders/{orderId}/orderItems
# Operation: getOrderItems
def getOrderItems(Endpoint, Restricted_data_token, orderId):
    # Set the url enpoint
    url = f"{Endpoint}/orders/v0/orders/{orderId}/orderItems"
    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "x-amz-access-token": Restricted_data_token,
    }

    # Handle response
    return get_json_response(url, headers)


# Extract shipment data
def extract_shipment_data(payload):
    package_detail = payload.get("packageDetail", {})
    cod_collection_method = payload.get("codCollectionMethod")
    marketplace_id = payload.get("marketplaceId")
    package_reference_id = package_detail.get("packageReferenceId")
    carrier_code = package_detail.get("carrierCode")
    carrier_name = package_detail.get("carrierName")
    shipping_method = package_detail.get("shippingMethod")
    tracking_number = package_detail.get("trackingNumber")
    ship_date = package_detail.get("shipDate")
    ship_from_supply_source_id = package_detail.get("shipFromSupplySourceId")
    order_items = payload.get("orderItems", [])

    return {
        "package_detail": package_detail,
        "cod_collection_method": cod_collection_method,
        "marketplace_id": marketplace_id,
        "package_reference_id": package_reference_id,
        "carrier_code": carrier_code,
        "carrier_name": carrier_name,
        "shipping_method": shipping_method,
        "tracking_number": tracking_number,
        "ship_date": ship_date,
        "ship_from_supply_source_id": ship_from_supply_source_id,
        "order_items": order_items,
    }


# Carrier Code
def carrierCode(analysis_code_2):
    if analysis_code_2 == "Proshipping":
        return "Royal Mail"
    elif analysis_code_2 == "DPD":
        return "DPD"
    elif analysis_code_2 == "DHL":
        return "DHL"
    else:
        return "Royal Mail"


# request_type [POST]
# Post tracking infomation to Amazon
def confirmShipment(Endpoint, access_token, orderId, payload):
    # Set the URL endpoint
    url = f"{Endpoint}/orders/v0/orders/{orderId}/shipmentConfirmation"

    # Set the headers
    headers = {
        # 'Content-Type': 'application/json',
        "x-amz-access-token": access_token
    }

    # Handle response
    try:
        # Post request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes

        # Return JSON response
        return response.json()
    except requests.RequestException as e:
        # Log the error for debugging purposes
        print(f"Request Exception: {e}")
        raise  # Re-raise the exception to be handled in the Django view
    except Exception as e:
        # Log the error for debugging purpose
        print(f"Error occurred: {e}")
        raise  # Re-raise the exception to be handled in the Django view


# Get marketplace id
def get_marketplace_id(country_code):
    marketplace_ids = {
        "ES": "A1RKKUPIHCS9HS",
        "UK": "A1F83G8C2ARO7P",
        "FR": "A13V1IB3VIYZZH",
        "BE": "AMEN7PMS3EDWL",
        "NL": "A1805IZSGTT6HS",
        "DE": "A1PA6795UKMFR9",
        "IT": "APJ6JRA9NG5V4",
        "SE": "A2NODRKZP88ZB9",
        "ZA": "AE08WJ6YKNBMC",
        "PL": "A1C3SOZRARQ6R3",
        "EG": "ARBP9OOSHTCHU",
        "TR": "A33AVAJ2PDY3EV",
        "SA": "A17E79C6D8DWNP",
        "AE": "A2VIGQ35RCS4UG",
        "IN": "A21TJRUUN4KGV",
    }

    return marketplace_ids.get(country_code, None)
