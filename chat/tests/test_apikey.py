import logging

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from chat.models import ChatUser, ChatRoom, APIKey, AIModel, AIVendor
from chat.utils import mask_api_key


class APIKeyViewTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.client = APIClient()

        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

        self.chat_user = ChatUser.objects.create(user=self.user, name=self.username)

        self.chatroom = ChatRoom.objects.create(
            name='Test Chat Room 1', owner=self.chat_user
        )

        self.ai_vendor = AIVendor.objects.create(name="Test AI Vendor")
        self.ai_model = AIModel.objects.create(
            name="Test AI Model", vendor=self.ai_vendor
        )

        self.api_key = APIKey.objects.create(
            owner=self.chat_user,
            key="sx-CJdBhagPQ5UTXRJsXmdOT4BlbkFJKAEyBi1FzHRSlWNJnPJD",
            desc="Test API Key",
            model=self.ai_model,
        )

    def test_get_apikey(self):
        self.client.force_login(self.user)

        url = reverse('api-key')
        response = self.client.get(url)
        content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('masked_api_keys', content)
        self.assertNotEqual(content['masked_api_keys'][0], self.api_key.key)

    def test_post_apikey(self):
        self.client.force_login(self.user)

        url = reverse('api-key')
        data = {
            'key': 'sx-CJdBhagPQ5UTXRJsXmdOT7BLbkFJKAEyBi1FzHRSlWNJnPJD',
            'desc': 'test_user_post_api_key',
            'model': 1,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        saved_api_key = APIKey.objects.all()[1]
        self.assertEqual(mask_api_key(saved_api_key.key), mask_api_key(data['key']))
