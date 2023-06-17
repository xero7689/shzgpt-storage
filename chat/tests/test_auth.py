import logging

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class CustomLoginViewTestCase(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_valid_login(self):
        # Create a test client and make a POST request to the login view
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': self.password})

        # Assert that the user is authenticated and the response is 'Logged in'
        self.assertTrue(response.content.decode().startswith('Logged in'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_username(self):
        # Create a test client and make a POST request to the login view with invalid username
        client = Client()
        response = client.post(reverse('login'), {'username': '', 'password': self.password})

        # Assert that the response is 'Username is required'
        self.assertEqual(response.content.decode(), 'Username is required')
        self.assertEqual(response.status_code, 200)

    def test_invalid_password(self):
        # Create a test client and make a POST request to the login view with invalid password
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': ''})

        # Assert that the response is 'Password is required'
        print(response.content.decode())
        self.assertEqual(response.content.decode(), 'Password is required')
        self.assertEqual(response.status_code, 200)

    def test_invalid_credentials(self):
        # Create a test client and make a POST request to the login view with invalid credentials
        client = Client()
        response = client.post(reverse('login'), {'username': 'invaliduser', 'password': 'invalidpass'})

        # Assert that the response is 'Invalid username or password'
        self.assertEqual(response.content.decode(), 'Invalid username or password')
        self.assertEqual(response.status_code, 200)