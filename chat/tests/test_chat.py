from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from chat.models import ChatRoom, ChatUser, Chat


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

    def test_delete_chat(self):
        self.client.force_login(self.user)
        chat_obj = Chat.objects.create(
            role="user", content="Unit Test Chat", tokens=3, chatroom=self.chatroom
        )
        url = reverse('chat-detail', kwargs={'pk': chat_obj.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Chat.objects.all()), 0)

    def tearDown(self):
        cache.clear()
        ChatRoom.objects.all().delete()
