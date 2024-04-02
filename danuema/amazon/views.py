# amazon/views.py

from datetime import datetime
import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views import View
from django.shortcuts import render
import requests

from amazon.constants import AMAZON_ENDPOINT, AMAZON_MARKET_ID
from amazon.models import Amazon_Order, Sage_SKU
from common.utils import amazon_sku_to_sage_sku
from danuema.settings import BASE_DIR
from sage.constants import SAGE_BASE_URL
from sage.views import create_sop_order, get_sage_order
from .utils import (
    carrierCode,
    confirmShipment,
    extract_shipment_data,
    get_access_token,
    getOrderAddress,
    getOrderBuyerInfo,
    getOrderItems,
    getOrders,
    get_restricted_token,
    getOrder,
    retrieve_orders,
)


# Get all Orders with items
# class OrdersItemsView(View):
#     def get(self, request):
#         # Retrieve query parameters from the request
#         access_token = get_access_token()
#         restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

#         try:
#             orders_data = getOrders(
#                 Endpoint=AMAZON_ENDPOINT,
#                 MarketplaceIds=AMAZON_MARKET_ID,
#                 Restricted_data_token=restricted_data_token,
#                 FulfillmentChannels="MFN",
#                 OrderStatuses="Unshipped"
#              )

#            # Iterate through orders and fetch order items for each order
#             orders_with_items = []
#             for order in orders_data['payload']['Orders']:
#                 order_id = order['AmazonOrderId']

#                 # Fetch order items with retry logic
#                 order_items_data = fetch_order_items_with_retry(order_id, restricted_data_token)

#                 # Iterate through order items and create Order objects if they don't exist already

#                 for order_item in order_items_data['payload']['OrderItems']:
#                     order_item_id = order_item['OrderItemId']

#                     order['OrderItems'] = order_items_data['payload']['OrderItems']
#                     orders_with_items.append(order)

#                     # transform sku
#                     sage_sku = amazon_sku_to_sage_sku(order_item['SellerSKU'])

#                     # Check if the order item already exists in the database
#                     if not Amazon_Order.objects.filter(order_item_id=order_item_id).exists():
#                         print('Order Id', order_item_id)
#                         Amazon_Order.objects.create(
#                             seller_sku=order_item['SellerSKU'],
#                             sage_sku = sage_sku,
#                             amazon_order_id=order['AmazonOrderId'],
#                             order_item_id=order_item_id,
#                             quantity_ordered=order_item['QuantityOrdered'],
#                             purchase_date=order['PurchaseDate'],
#                             unshipped= order['OrderStatus']
#                         )


#             # Create the final response payload
#             response_data = {
#                 "payload": {
#                     "Orders": orders_with_items,
#                 }
#             }

#             # return response
#             return JsonResponse(response_data, status=200)
#             # return success response
#             # return JsonResponse({'message': 'Orders created successfully'}, status=200)
#         except Exception as e:
#             # Log the error for debugging purposes
#             print(f"Error occurred: {e}")
#             return JsonResponse({'error': 'Internal Server Error'}, status=500)


# # create function to transform amazon sku to sage
# def amazon_sku_to_sage_sku(amazon_sku):
#     try:
#         # Lookup the Amazon SKU in the Sage_SKU database
#         sage_sku_objs = Sage_SKU.objects.filter(Q(amazon_sku=amazon_sku) | Q(amazon_sku=amazon_sku + '*'))
#         if sage_sku_objs.exists():
#             # If multiple objects found, choose one arbitrarily or based on your criteria
#             sage_sku_obj = sage_sku_objs.first()
#             sage_sku = sage_sku_obj.sage_sku
#         else:
#             # If not found, use the Amazon SKU itself
#             sage_sku = amazon_sku
#     except Sage_SKU.DoesNotExist:
#         # If Sage_SKU object doesn't exist, use the Amazon SKU itself
#         sage_sku = amazon_sku

#     return sage_sku


# Get All Orders View
class AllOrdersView(View):
    def get(self, request):
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)
        fulfillmentChannels = "MFN"
        OrderStatuses = "Unshipped"

        try:
            orders_data = getOrders(
                Endpoint=AMAZON_ENDPOINT,
                MarketplaceIds=AMAZON_MARKET_ID,
                Restricted_data_token=restricted_data_token,
                FulfillmentChannels=fulfillmentChannels,
                OrderStatuses=OrderStatuses,
            )

            # Iterate through orders and fetch order items for each order
            orders_with_items = []
            for order in orders_data["payload"]["Orders"]:
                order_id = order["AmazonOrderId"]
                order_items_data = getOrderItems(
                    Endpoint=AMAZON_ENDPOINT,
                    Restricted_data_token=restricted_data_token,
                    orderId=order_id,
                )
                order["OrderItems"] = order_items_data["payload"]["OrderItems"]
                orders_with_items.append(order)

            # Create the final response payload
            response_data = {
                "payload": {
                    "Orders": orders_with_items,
                }
            }

            # return response
            return JsonResponse(response_data, status=200)
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get Orders View
class OrdersView(View):
    def get(self, request):
        # Retrieve query parameters from the request

        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrders(
                Endpoint=AMAZON_ENDPOINT,
                MarketplaceIds=AMAZON_MARKET_ID,
                Restricted_data_token=restricted_data_token,
                FulfillmentChannels="MFN",
                OrderStatuses="Unshipped",
            )

            # return response
            return JsonResponse(orders_data, status=200)
        except Exception as e:
            # Log he error for debugging purpose
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get Order Items
class OrderItems(View):
    def get(self, request, orderId):
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrderItems(
                Endpoint=AMAZON_ENDPOINT,
                Restricted_data_token=restricted_data_token,
                orderId=orderId,
            )

            # return response
            return JsonResponse(orders_data, status=200)
        except Exception as e:
            # Log he error for debugging purpose
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get Single Order View
class SingleOrderView(View):
    def get(self, request, orderId):
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrder(
                Endpoint=AMAZON_ENDPOINT,
                Restricted_data_token=restricted_data_token,
                orderId=orderId,
            )

            # return response
            return JsonResponse(orders_data, status=200)
        except Exception as e:
            # Log he error for debugging purpose
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get Order Buyer Info View
class OrderBuyerInfoView(View):
    def get(self, request, orderId):
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrderBuyerInfo(
                Endpoint=AMAZON_ENDPOINT,
                Restricted_data_token=restricted_data_token,
                orderId=orderId,
            )

            # return response
            return JsonResponse(orders_data, status=200)
        except Exception as e:
            # Log he error for debugging purpose
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get Order Buyer Address Info View
class OrderAdressInfoView(View):
    def get(self, request, orderId):
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrderAddress(
                Endpoint=AMAZON_ENDPOINT,
                Restricted_data_token=restricted_data_token,
                orderId=orderId,
            )

            # return response
            return JsonResponse(orders_data, status=200)
        except Exception as e:
            # Log he error for debugging purpose
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


class CreateSageOrders(View):

    def get(self, request):
        try:
            # Get Amazon orders data
            amazon_response = get_all_orders(
                FulfillmentChannels="MFN", OrderStatuses="Unshipped"
            )

            # Extract JSON data from the response
            amazon_data = json.loads(amazon_response.content)

            # Check if 'payload' key exists in the data
            if "payload" in amazon_data:
                orders = amazon_data["payload"].get("Orders", [])
            else:
                orders = []

            # Call create_sop_order function with the entire payload
            response = create_sop_order(request, amazon_data)

            return response

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {e}"}, status=500)


############ Start Sage Posting

############################ End SOP Orders

############ End Sage Posting


def get_all_orders(FulfillmentChannels, OrderStatuses):
    access_token = get_access_token()
    restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)
    # fulfillmentChannels = "MFN"
    # OrderStatuses = "Unshipped"

    try:
        orders_data = getOrders(
            Endpoint=AMAZON_ENDPOINT,
            MarketplaceIds=AMAZON_MARKET_ID,
            Restricted_data_token=restricted_data_token,
            FulfillmentChannels=FulfillmentChannels,
            OrderStatuses=OrderStatuses,
        )

        # Iterate through orders and fetch order items for each order
        # orders_with_items = []
        # for order in orders_data["payload"]["Orders"]:
        #     order_id = order["AmazonOrderId"]
        #     order_items_data = getOrderItems(
        #         Endpoint=AMAZON_ENDPOINT,
        #         Restricted_data_token=restricted_data_token,
        #         orderId=order_id,
        #     )
        #     order["OrderItems"] = order_items_data["payload"]["OrderItems"]
        #     orders_with_items.append(order)

        # Iterate through orders and fetch order items for each order
        orders_with_items = []
        for order in orders_data["payload"]["Orders"]:
            order_id = order["AmazonOrderId"]

            # Fetch order items with retry logic
            order_items_data = fetch_order_items_with_retry(
                order_id, restricted_data_token
            )

            new_order_items = []
            for order_item in order_items_data["payload"]["OrderItems"]:
                order_item_id = order_item["OrderItemId"]
                # Check if any order items are not already in the database
                if not Amazon_Order.objects.filter(
                    order_item_id=order_item_id
                ).exists():
                    new_order_items.append(order_item)

            if new_order_items:
                # Add order only if it has new items
                order["OrderItems"] = new_order_items
                orders_with_items.append(order)

                # # Iterate through new order items and create Amazon_Order objects
                # for order_item in new_order_items:
                # sage_sku = amazon_sku_to_sage_sku(order_item["SellerSKU"])
                # Amazon_Order.objects.create(
                #     seller_sku=order_item["SellerSKU"],
                #     sage_sku=sage_sku,
                #     amazon_order_id=order["AmazonOrderId"],
                #     order_item_id=order_item["OrderItemId"],
                #     quantity_ordered=order_item["QuantityOrdered"],
                #     purchase_date=order["PurchaseDate"],
                #     unshipped=order["OrderStatus"],
                # )

        # Create the final response payload
        response_data = {
            "payload": {
                "Orders": orders_with_items,
            }
        }

        # return response
        return JsonResponse(response_data, status=200)
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error occurred: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# Get order items
def orders_items(request):
    if request.method == "GET":
        # Retrieve query parameters from the request
        access_token = get_access_token()
        restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            orders_data = getOrders(
                Endpoint=AMAZON_ENDPOINT,
                MarketplaceIds=AMAZON_MARKET_ID,
                Restricted_data_token=restricted_data_token,
                FulfillmentChannels="MFN",
                OrderStatuses="Unshipped",
            )

            # Iterate through orders and fetch order items for each order
            orders_with_items = []
            for order in orders_data["payload"]["Orders"]:
                order_id = order["AmazonOrderId"]

                # Fetch order items with retry logic
                order_items_data = fetch_order_items_with_retry(
                    order_id, restricted_data_token
                )

                new_order_items = []
                for order_item in order_items_data["payload"]["OrderItems"]:
                    order_item_id = order_item["OrderItemId"]
                    # Check if any order items are not already in the database
                    if not Amazon_Order.objects.filter(
                        order_item_id=order_item_id
                    ).exists():
                        new_order_items.append(order_item)

                if new_order_items:
                    # Add order only if it has new items
                    order["OrderItems"] = new_order_items
                    orders_with_items.append(order)

                    # Iterate through new order items and create Amazon_Order objects
                    for order_item in new_order_items:
                        sage_sku = amazon_sku_to_sage_sku(order_item["SellerSKU"])
                        Amazon_Order.objects.create(
                            seller_sku=order_item["SellerSKU"],
                            sage_sku=sage_sku,
                            amazon_order_id=order["AmazonOrderId"],
                            order_item_id=order_item["OrderItemId"],
                            quantity_ordered=order_item["QuantityOrdered"],
                            purchase_date=order["PurchaseDate"],
                            unshipped=order["OrderStatus"],
                        )

            # Create the final response payload
            response_data = {
                "payload": {
                    "Orders": orders_with_items,
                }
            }

            # return response
            return JsonResponse(response_data, status=200)
            # return success response
            # return JsonResponse({'message': 'Orders created successfully'}, status=200)
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error occurred: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)


# fetch order items
def fetch_order_items_with_retry(order_id, restricted_data_token, max_retries=5):
    """
    Fetch order items from Amazon API with retry logic in case of rate limiting.

    Args:
    - order_id: The ID of the order for which to fetch items.
    - restricted_data_token: The token for accessing restricted data in the Amazon API.
    - max_retries: Maximum number of retry attempts. Default is 5.

    Returns:
    - order_items_data: The data containing order items.
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            order_items_data = getOrderItems(
                Endpoint=AMAZON_ENDPOINT,
                Restricted_data_token=restricted_data_token,
                orderId=order_id,
            )
            return order_items_data  # Return if no error occurred
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded, retry with increasing delay
                retry_count += 1
                delay = min(
                    2**retry_count, 30
                )  # Exponential backoff with maximum delay of 30 seconds
                time.sleep(delay)
            else:
                raise e  # Re-raise any other HTTP errors

    # If all retries failed, log an error and return None
    print(
        f"Failed to fetch order items for order {order_id} after {max_retries} retries."
    )
    return None


# Handle sage amazon tracking


# Post Shipment Confirmation
class ConfirmShipmentView(View):
    def post(self, request, orderId):

        access_token = get_access_token()
        # restricted_data_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

        try:
            payload = json.loads(request.body)
            shipment_data = extract_shipment_data(payload)
            Endpoint = (AMAZON_ENDPOINT,)
            # Perform the shipment confirmation logic here
            response_data = confirmShipment(
                Endpoint, access_token, orderId, payload=shipment_data
            )

            # You can update your database or perform any other required operations

            # Respond with a success message
            # response_data = {
            #     'message': f'Shipment confirmed for order {orderId}'
            # }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data in request body"}, status=400
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# POST /orders/v0/orders/{orderId}/shipmentConfirmation
# Operation: confirmShipment
# def sage_amazon_tracking(request):
#     # Fetch all unshipped orders from the amazon database
#     # Loop trough each amazon order in the database
#     # Get Order from Sage
#     # Check if the consignment number which is the analysis_code_4 is not empty
#     # Then get the database information from the amazon id
#     # Post the tracking information to amazon
#     # On Successfull posting change database info to shipped
#     order_id = "203-1566897-3013600"

#     try:

#         unshipped_orders = Amazon_Order.objects.filter(
#             unshipped=Amazon_Order.UN_SHIPPED
#         )

#         temp = []
#         # loop through unshipped items
#         for order in unshipped_orders:

#             seller_sku = order.seller_sku
#             sage_sku = order.sage_sku
#             amazon_order_id = order.amazon_order_id
#             order_item_id = order.order_item_id
#             quantity_ordered = order.quantity_ordered
#             purchase_date = order.purchase_date.strftime("%Y-%m-%d %H:%M:%S")
#             unshipped = order.unshipped

#             if amazon_order_id in temp:
#                 continue

#             sage_response = get_sage_order(amazon_order_id)

#             sage_order = json.loads(sage_response.content)[0]

#             # Get order
#             # packageReferenceId = sage_order["id"]  # id from sage
#             packageReferenceId = sage_order[
#                 "document_no"
#             ]  # Use amazon id as the refrence id
#             shippingMethod = "SHIPPING"
#             trackingNumber = sage_order["analysis_code_4"]
#             shipDate = sage_order["analysis_code_11"]
#             carrier = carrierCode(sage_order["analysis_code_2"])  # carrier from sage
#             lines = sage_order["lines"]

#             # if trackingNumber == "":
#             #     continue

#             items = []

#             for line in lines:
#                 item = {}
#                 code = line["code"]
#                 if code == "Carriage":
#                     continue
#                 item["orderItemId"] = line["analysis_code_12"]
#                 item["quantity"] = line["line_quantity"]
#                 items.append(item)

#                 payload = {
#                     "marketplaceId": AMAZON_MARKET_ID,
#                     "packageDetail": {
#                         "packageReferenceId": packageReferenceId,
#                         "carrierCode": carrier,
#                         "carrierName": carrier,
#                         "shippingMethod": shippingMethod,
#                         "trackingNumber": trackingNumber,
#                         "shipDate": shipDate,
#                         "orderItems": items,
#                     },
#                 }

#                 print(payload)

#             # Fetch all unshipped orders with the given Amazon ID
#             # unshipped_order = Amazon_Order.objects.filter(
#             #     amazon_order_id=amazon_order_id, unshipped=Amazon_Order.UN_SHIPPED
#             # )

#             unshipped_order = Amazon_Order.objects.filter(
#                 amazon_order_id=amazon_order_id
#             )

#             # Update the status of each unshipped order to Shipped
#             for order in unshipped_order:
#                 order.unshipped = Amazon_Order.SHIPPED
#                 # Update other fields if needed, e.g., tracking information, shipping date, etc.
#                 order.save()

#             temp.append(
#                 amazon_order_id
#             )  # Update the amazon order with the same amazon id once

#         #     return sage_response

#         # path = f"/orders/v0/orders/{orderId}/shipmentConfirmation"
#         # body = {}
#         # packageDetail = ""  # Properties of packages
#         # # marketplaceId


#         return JsonResponse(payload)

#         return JsonResponse({"message": "Tracking information posted successfully."})
#     except Exception as e:
#         return JsonResponse({"error": f"An error occured: {e}"}, status=500)


def sage_amazon_tracking(request):

    try:
        print("am here")

        access_token = get_access_token()

        unshipped_orders = Amazon_Order.objects.filter(
            unshipped=Amazon_Order.UN_SHIPPED
        )

        temp = []

        for order in unshipped_orders:
            seller_sku = order.seller_sku
            sage_sku = order.sage_sku
            amazon_order_id = order.amazon_order_id
            order_item_id = order.order_item_id
            quantity_ordered = order.quantity_ordered
            purchase_date = order.purchase_date.strftime("%Y-%m-%d %H:%M:%S")
            unshipped = order.unshipped

            if amazon_order_id in temp:
                continue

            # Get sage order for the amazon id
            sage_response = get_sage_order(amazon_order_id)

            sage_order = json.loads(sage_response.content)[0]

            # print(sage_order)

            packageReferenceId = int(
                sage_order["document_no"]
            )  # Use amazon id as the reference id
            shippingMethod = "SHIPPING"
            trackingNumber = sage_order["analysis_code_4"]
            shipDate = sage_order["analysis_code_11"]
            carrier = carrierCode(sage_order["analysis_code_2"])  # carrier from sage
            lines = sage_order["lines"]

            if trackingNumber == "":
                continue

            items = []

            for line in lines:
                item = {}
                code = line["code"]
                if code == "Carriage":
                    continue
                item["orderItemId"] = line["analysis_code_12"]
                item["quantity"] = int(line["line_quantity"])
                items.append(item)

            iso_date = datetime.strptime(shipDate, "%d/%m/%Y").strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

            payload = {
                "marketplaceId": "A1F83G8C2ARO7P",
                "packageDetail": {
                    "packageReferenceId": packageReferenceId,
                    "carrierCode": carrier,
                    "carrierName": carrier,
                    "shippingMethod": shippingMethod,
                    "trackingNumber": trackingNumber,
                    "shipDate": iso_date,  # Convert to ISO 8601 format,
                    "orderItems": items,
                },
            }

            # print("payload", payload)

            # Post the payload
            path_name = f"/orders/v0/orders/{amazon_order_id}/shipmentConfirmation"
            url = f"{AMAZON_ENDPOINT}{path_name}"
            response = requests.post(
                f"https://sellingpartnerapi-eu.amazon.com/orders/v0/orders/{amazon_order_id}/shipmentConfirmation",
                headers={"x-amz-access-token": access_token},
                json=payload,
            )

            print("response", response)

            response.raise_for_status()
            print(
                f"Successfully sent shipment confirmation for order {amazon_order_id}"
            )

            # Check if the request was successful

            # Update the status of each unshipped order to Shipped
            unshipped_order = Amazon_Order.objects.filter(
                amazon_order_id=amazon_order_id
            )
            for order in unshipped_order:
                order.unshipped = Amazon_Order.SHIPPED
                order.save()

            temp.append(
                amazon_order_id
            )  # Update the amazon order with the same amazon id once

            # return JsonResponse(payload)

        return JsonResponse({"message": "Tracking information posted."})

    except Exception as e:
        return JsonResponse({"error": f"An error occured: {e}"}, status=500)
