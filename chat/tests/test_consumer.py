from unittest.mock import MagicMock, patch
from datetime import datetime

import orjson
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from chat.consumers import AsyncChatConsumer
from chat.models import ChatRoom, ChatUser
from chat.schema import ChatContext, ChatRequest, ChatResponse, ChatRole


class SocketServerTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"

        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.chat_user = ChatUser.objects.create(user=self.user, name="test-chat-user")

        self.chatroom = ChatRoom.objects.create(
            name="Test Chat Room 1", owner=self.chat_user
        )

        self.client = Client()
        self.client.force_login(user=self.user)
        self.client.post(
            reverse("login"), {"username": self.username, "password": self.password}
        )

    @patch("chat.consumers.OpenAILLM")
    async def test_my_consumer(self, MockOpenAIAPIWrapper):
        gpt_content_mock = "This is a mock GPT response"
        api_wrapper_mock = MagicMock()
        api_wrapper_mock.response_content = gpt_content_mock
        api_wrapper_mock.response_tokens = 17
        MockOpenAIAPIWrapper.return_value = api_wrapper_mock

        headers = [
            (b"origin", b"..."),
            (b"cookie", self.client.cookies.output(header="", sep="; ").encode()),
        ]

        communicator = WebsocketCommunicator(
            AsyncChatConsumer.as_asgi(), "/test/", headers
        )
        communicator.scope["user"] = self.user
        communicator.scope["session"] = self.client.session

        connected, subprotocol = await communicator.connect()
        assert connected

        context = ChatContext(
            chatroom_id=self.chatroom.id, role=ChatRole.USER, content="Hello World"
        )
        timestamp = int(datetime.now().timestamp())
        chat_request = ChatRequest(context=context, timestamp=timestamp)

        await communicator.send_json_to(chat_request.model_dump())
        response = await communicator.receive_from()

        response = ChatResponse.model_validate(orjson.loads(response))

        self.assertEqual(response.context.chatroom_id, self.chatroom.id)
        self.assertEqual(response.context.content, gpt_content_mock)
        self.assertEqual(response.context.role, ChatRole.ASSISTANT)

        await communicator.disconnect()
