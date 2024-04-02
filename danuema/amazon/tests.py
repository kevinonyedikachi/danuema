from django.http import JsonResponse
from django.test import TestCase
from amazon.constants import AMAZON_ENDPOINT, AMAZON_MARKET_ID

from amazon.utils import get_access_token, get_restricted_token, retrieve_orders


# Create your tests here.
# Create a test view to access token
def text_access_token(request):
    access_token = get_access_token()
    if access_token:
        return JsonResponse({"access_token": access_token})
    else:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=500)


# Create test restricted token view
def test_restricted_token(request):
    # Retrieve the access token first
    access_token = get_access_token()

    # Attempt to get the restricted token
    restricted_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

    if restricted_token:
        return JsonResponse({"restricted_token": restricted_token})
    else:
        return JsonResponse(
            {"error": "Failed to retrieve restricted token"}, status=500
        )


def test_retrieve_orders(request):
    # Get the required arguments from wherever they are stored
    # Retrieve the access token first
    access_token = get_access_token()

    # Attempt to get the restricted token
    restricted_token = get_restricted_token(access_token, AMAZON_ENDPOINT)

    # Call the retrieve_orders function with the arguments
    orders_data = retrieve_orders(AMAZON_ENDPOINT, AMAZON_MARKET_ID, restricted_token)

    if orders_data:
        # Return the orders data as a JSON response
        return JsonResponse({"orders": orders_data})
    else:
        return JsonResponse({"error": "Failed to retrieve orders"})
