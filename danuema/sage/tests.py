# tests.py
from django.test import TestCase
from django.urls import reverse
from sage.models import RefreshToken  # Import your RefreshToken model
from unittest.mock import patch

class AccessTokenTestCase(TestCase):
    def setUp(self):
        # Create a sample refresh token in the database
        self.refresh_token = RefreshToken.objects.create(token='sample_refresh_token')

    @patch('sage.views.get_access_token_from_refresh')
    def test_access_token_view(self, mock_get_access_token_from_refresh):
        # Mock the get_access_token_from_refresh function to return a sample access token and a new refresh token
        mock_get_access_token_from_refresh.return_value = 'sample_access_token', 'new_refresh_token'

        # Get the URL for the access token view
        url = reverse('get_access_token')

        # Make a GET request to the access token view
        response = self.client.get(url)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the access token and new refresh token
        self.assertIn(b"Access Token: sample_access_token", response.content)
        self.assertIn(b"New Refresh Token: new_refresh_token", response.content)

        # Check that the refresh token has been updated in the database
        updated_refresh_token = RefreshToken.objects.get(id=self.refresh_token.id)
        self.assertEqual(updated_refresh_token.token, 'new_refresh_token')
# v1.MemX4S3HQxcdwKkBk2uGN8Ta8DQnXvCLUR1ee0c1ls9R2A0RXX3tOmqJkjrlcYSrK3MC6EH_xhGfnC_XV9xBL_0