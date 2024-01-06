from unittest.mock import MagicMock, patch

from django.test import TestCase, Client
from django.urls import reverse

from channels.testing import WebsocketCommunicator
from chat.consumers import AsyncChatConsumer

from django.contrib.auth.models import User
from chat.models import ChatUser, ChatRoom

from common.pb.message_pb2 import ChatRequest, ChatResponse, ChatRoleType


class SocketServerTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass'

        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.chat_user = ChatUser.objects.create(user=self.user, name='test-chat-user')

        self.chatroom = ChatRoom.objects.create(
            name='Test Chat Room 1', owner=self.chat_user
        )

        self.client = Client()
        self.client.force_login(user=self.user)
        self.client.post(
            reverse('login'), {'username': self.username, 'password': self.password}
        )

    @patch('chat.consumers.OpenAILLM')
    async def test_my_consumer(self, MockOpenAIAPIWrapper):
        gpt_content_mock = "This is a mock GPT response"
        api_wrapper_mock = MagicMock()
        api_wrapper_mock.response_content = gpt_content_mock
        api_wrapper_mock.response_tokens = 17
        MockOpenAIAPIWrapper.return_value = api_wrapper_mock

        headers = [
            (b'origin', b'...'),
            (b'cookie', self.client.cookies.output(header='', sep='; ').encode()),
        ]

        communicator = WebsocketCommunicator(
            AsyncChatConsumer.as_asgi(), "/test/", headers
        )
        communicator.scope["user"] = self.user
        communicator.scope["session"] = self.client.session

        connected, subprotocol = await communicator.connect()
        assert connected

        chat = ChatRequest()
        chat.context.chatroom_id = self.chatroom.id
        chat.context.role = ChatRoleType.USER
        chat.context.content = "Hi GPT! Say 'This is message from websocket'"

        await communicator.send_to(bytes_data=chat.SerializeToString())
        response = await communicator.receive_from()
        response = ChatResponse.FromString(response)

        self.assertEqual(response.context.chatroom_id, self.chatroom.id)
        self.assertEqual(response.context.content, gpt_content_mock)
        self.assertEqual(response.context.role, ChatRoleType.ASSISTANT)

        await communicator.disconnect()
