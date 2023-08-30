import json
import logging

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from chat.models import ChatUser

class CustomLoginViewTestCase(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.chat_user = ChatUser.objects.create(
            user=self.user, name='test-chat-user')

    def test_valid_login(self):
        # Create a test client and make a POST request to the login view
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': self.password})

        # Assert that the user is authenticated and the response is 'Logged in'
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json['status'], 'succeeded')
        self.assertEqual(response.status_code, 200)

    def test_invalid_username(self):
        # Create a test client and make a POST request to the login view with invalid username
        client = Client()
        response = client.post(reverse('login'), {'username': '', 'password': self.password})

        # Assert that the response is 'Username is required'
        self.assertEqual(response.content.decode(), '{"status": "failed", "detail": "Username/Password is required", "data": {}}')
        self.assertEqual(response.status_code, 401)

    def test_invalid_password(self):
        # Create a test client and make a POST request to the login view with invalid password
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': ''})

        # Assert that the response is 'Password is required'
        print(response.content.decode())
        self.assertEqual(response.content.decode(), '{"status": "failed", "detail": "Username/Password is required", "data": {}}')
        self.assertEqual(response.status_code, 401)

    def test_invalid_credentials(self):
        # Create a test client and make a POST request to the login view with invalid credentials
        client = Client()
        response = client.post(reverse('login'), {'username': 'invaliduser', 'password': 'invalidpass'})

        # Assert that the response is 'Invalid username or password'
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json['status'], 'failed')
        self.assertEqual(response.status_code, 401)
