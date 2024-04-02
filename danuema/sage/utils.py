import logging
import requests
from django.core.exceptions import ObjectDoesNotExist
from sage.models import RefreshToken


# Initialise logger
logger = logging.getLogger(__name__)

# Get sage access token
def get_access_token():

    client_id = 'XqUEiGFlwYG3iGxlseFfgVWQHM14tjDR'
    client_secret = '9tAPWs0Z1JVrYRGSYVZsAaCh2PAkouj5ZnU8x4MiAQyolRwmgcH2kl-ew5IiV_9F'
    redirect_uri = 'https://sage200nativeapi-nesmailorder.msappproxy.net/Sage200NativeAPI/'

    try:
        # Load the refresh token from the database
        refresh_token = load_refresh_token()
        if not refresh_token:
            raise ValueError("No refresh token found in the database.")

        # Get the access token and new refresh token
        access_token, new_refresh_token = get_access_token_from_refresh(client_id, client_secret, redirect_uri, refresh_token)

        # Save the new refresh token for subsequent requests
        if new_refresh_token:
            save_refresh_token(new_refresh_token)

        # Return a dictionary containing the access token
        return {"access_token": access_token}
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise
    except requests.RequestException as re:
        logger.error(f"RequestException: {re}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while fetching access token: {e}")
        raise

# Get sage refresh token
def get_access_token_from_refresh(client_id, client_secret, redirect_uri, refresh_token):
    url = "https://id.sage.com/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(url, data=payload)
    response_json = response.json()

    if 'access_token' in response_json and 'refresh_token' in response_json:
        return response_json['access_token'], response_json['refresh_token']
    else:
        raise ValueError("Failed to get access token from refresh token.")

# Save refresh token to database
def save_refresh_token(refresh_token):
    RefreshToken.objects.update(token=refresh_token)

# Load the refresh token
def load_refresh_token():
    try:
        refresh_token = RefreshToken.objects.latest('id').token
        return refresh_token
    except ObjectDoesNotExist:
        return None


































# # Function to authenticate with Sage API and retrieve access token
# def authenticate_with_sage(client_id, client_secret, redirect_uri, authorization_code):
#     token_url = 'https://id.sage.com/oauth/token'
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     data = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'redirect_uri': redirect_uri,
#         'code': authorization_code,
#         'grant_type': 'authorization_code'
#     }

#     response = requests.post(token_url, headers=headers, data=data)

#     if response.status_code == 200:
#         return response.json()['access_token']
#     else:
#         raise Exception('Failed to authenticate with Sage API')
    

# # Funtion to refresh access token
# def refresh_access_token(client_id, client_secret, redirect_uri, refresh_token):
#     token_url = 'https://id.sage.com/oauth/token'
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     data = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'redirect_uri': redirect_uri,
#         'refresh_token': refresh_token,
#         'grant_type': 'refresh_token'
#     }

#     response = requests.post(token_url, headers=headers, data=data)

#     if response.status_code == 200:
#         return response.json()['access_token']
#     else:
#         raise Exception('Failed to refresh access token')
    


############################################## To make authenticated requests to the Sage API using the access token

BASE_URL = 'https://api.columbus.sage.com/uk/sage200extra/accounts/v1'  # Adjust the base URL based on the Sage application

def make_authenticated_request(endpoint, access_token, method='GET', data=None):
    url = f'{BASE_URL}/{endpoint}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Company': 'your_company_id',  # Replace with your company ID
        'X-Site': 'your_site_id'  # Replace with your site ID
    }

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError('Invalid HTTP method')

        response.raise_for_status()  # Raise exception for non-200 status codes

        return response.json()
    except requests.RequestException as e:
        raise Exception(f'Error making authenticated request: {str(e)}')
