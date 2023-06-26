from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timezone, timedelta
from chat.models import ChatRoom, Chat, ChatUser
from chat.serializer import ChatSerializer


class ChatHistoryAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        self.chat_user = ChatUser.objects.create(
            user=self.user, name='test-chat-user')
        self.chatroom = ChatRoom.objects.create(
            name='Test Chat Room', owner=self.chat_user)
        self.chat = Chat.objects.create(
            chatroom=self.chatroom,
            role='user',
            content='First test content',
            created_at=datetime.strptime(
                '2022-01-01 12:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        )

    def test_chat_history_retrieve_latest_messages(self):
        url = reverse('chat-history', kwargs={'chatroom_id': self.chatroom.pk})
        self.client.force_login(self.user)
        response = self.client.get(url, format='json')
        chat_serializer = ChatSerializer(Chat.objects.filter(
            chatroom=self.chatroom).order_by('-created_at')[:20], many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, chat_serializer.data)

    def test_chat_history_retrieve_messages_with_date_filters(self):
        url = reverse('chat-history', kwargs={'chatroom_id': self.chatroom.pk})
        self.client.force_login(self.user)
        start_date = datetime.strptime(
            '2021-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(
            '2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        response = self.client.get(
            url + f'?date_gte={start_date.strftime("%Y-%m-%d %H:%M:%S")}&date_lt={end_date.strftime("%Y-%m-%d %H:%M:%S")}', format='json')
        chat_serializer = ChatSerializer(Chat.objects.filter(
            chatroom=self.chatroom, created_at__gte=start_date, created_at__lt=end_date).order_by('-created_at'), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, chat_serializer.data)

    def test_chat_history_retrieve_messages_with_date_gte_filter(self):
        url = reverse('chat-history', kwargs={'chatroom_id': self.chatroom.pk})
        self.client.force_login(self.user)
        start_date = datetime.strptime(
            '2021-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        response = self.client.get(
            url + f'?date_gte={start_date.strftime("%Y-%m-%d %H:%M:%S")}', format='json')
        chat_serializer = ChatSerializer(Chat.objects.filter(
            chatroom=self.chatroom, created_at__gte=start_date).order_by('-created_at'), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, chat_serializer.data)

    def test_chat_history_retrieve_messages_with_date_lt_filter(self):
        url = reverse('chat-history', kwargs={'chatroom_id': self.chatroom.pk})
        self.client.force_login(self.user)
        end_date = datetime.strptime(
            '2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        response = self.client.get(
            url + f'?date_lt={end_date.strftime("%Y-%m-%d %H:%M:%S")}', format='json')
        chat_serializer = ChatSerializer(Chat.objects.filter(
            chatroom=self.chatroom, created_at__lt=end_date).order_by('-created_at'), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, chat_serializer.data)

    def test_chat_history_retrieve_messages_with_invalid_chatroom_id(self):
        url = reverse('chat-history',
                      kwargs={'chatroom_id': self.chatroom.pk + 1})
        self.client.force_login(self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['detail'], 'Invalid Chatroom ID')

    def test_chat_history_retrieve_messages_with_invalid_date_format(self):
        url = reverse('chat-history', kwargs={'chatroom_id': self.chatroom.pk})
        self.client.force_login(self.user)
        response = self.client.get(
            url + '?date_gte=2021-13-01 00:00:00', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
