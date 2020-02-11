from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# here API URLs are defined
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


# create user helper function
def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'password',
            'name': 'Test Name'
        }
        self.invalid_payload_password = {
            'email': 'test@example.com',
            'password': 'pass',
            'name': 'Test Name'
        }
        self.invalid_payload_no_password = {
            'email': 'test@example.com',
            'password': '',
            'name': 'Test Name'
        }
        self.invalid_payload_no_email = {
            'email': '',
            'password': 'password',
            'name': 'Test Name'
        }

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        res = self.client.post(CREATE_USER_URL, self.valid_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.valid_payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        create_user(**self.valid_payload)
        res = self.client.post(CREATE_USER_URL, self.valid_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be at least 8 characters long"""
        res = self.client.post(CREATE_USER_URL, self.invalid_payload_password)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=self.invalid_payload_password['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**self.valid_payload)
        res = self.client.post(TOKEN_URL, self.valid_payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(**self.valid_payload)
        res = self.client.post(TOKEN_URL, self.invalid_payload_password)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        res = self.client.post(TOKEN_URL, self.valid_payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', res.data)

    def test_create_token_missing_password(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, self.invalid_payload_no_password)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', res.data)

    def test_create_token_missing_email(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, self.invalid_payload_no_email)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)
