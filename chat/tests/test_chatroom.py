from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from chat.models import ChatRoom, ChatUser


class ChatRoomAPIViewTest(TestCase):
    def setUp(self):
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

    def test_get_queryset(self):
        self.client.force_login(self.user)
        url = reverse('chatrooms')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['name'], 'Test Chat Room 1')

        queryset_cache_key = f'views.queryset.cache.chatroomapi.{self.user}'
        self.assertEqual(len(cache.get(queryset_cache_key)), 1)

    def test_create_chat_room(self):
        self.client.force_login(self.user)
        new_chatroom_name = 'Test Chat Room 2'
        url = reverse('chatrooms')
        response = self.client.post(url, {'name': new_chatroom_name})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChatRoom.objects.count(), 2)

        cached_queryset = cache.get(f'views.queryset.cache.chatroomapi.{self.user}')

        self.assertIsNotNone(cached_queryset)
        self.assertEqual(len(cached_queryset), 2)
        self.assertEqual(cached_queryset[1].owner, self.chat_user)
        self.assertEqual(cached_queryset[1].name, new_chatroom_name)

    def tearDown(self):
        cache.clear()
        ChatRoom.objects.all().delete()
