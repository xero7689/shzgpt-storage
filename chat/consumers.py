import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import login

from chat.models import APIKey, Chat, ChatRoom

from common.api_wrapper import OpenAIAPIWrapper
from common.utils import formate_chats_to_gpt_request_messages
from common.pb.message_pb2 import ChatRequest, ChatResponse, StatusCode, ChatRoleType

from google.protobuf.json_format import Parse, MessageToJson


logger = logging.getLogger(__name__)


class AsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f"chat_{self.user}"

        # Join Group
        # Place current channel to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data):
        await login(self.scope, self.scope['user'])

        request = ChatRequest()
        request.ParseFromString(bytes_data)
        message = MessageToJson(request)

        # Receive data from socket and send to the channels layer
        # This will transform chat.message to chat_message defined below
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "return.gpt.message",
                "message": message
            }
        )

    @database_sync_to_async
    def get_api_key(self):
        return APIKey.objects.first()

    @database_sync_to_async
    def get_recent_chat_messages(self, request, cal_num=10):
        chatroom_id = request.context.chatroom_id
        recent_messages = Chat.objects.filter(
            chatroom=chatroom_id).order_by('-created_at')[:cal_num]
        return list(recent_messages)

    @database_sync_to_async
    def save_request_chat_message(self, request):
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        request_chat_message = Chat(
            role="user", content=request.context.content, chatroom=chatroom)
        request_chat_message.save()

    @database_sync_to_async
    def save_gpt_response_message(self, request, content):
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        gpt_response_message = Chat(
            role="assistant", content=content, chatroom=chatroom)
        gpt_response_message.save()

    def build_gpt_message_response(self, request, content, serialize=True):
        response = ChatResponse()

        response.status_code = StatusCode.SUCCESS
        response.context.chatroom_id = request.context.chatroom_id
        response.context.content = content
        response.context.role = ChatRoleType.ASSISTANT
        response.status_detail = ""
        response.context.timestamp.GetCurrentTime()

        if serialize is True:
            return response.SerializeToString()
        return response

    def build_gpt_message_response_rr(self, request, content, serialize=True):
        response = ChatResponse()

        response.status_code = StatusCode.FAILED
        response.context.chatroom_id = request.context.chatroom_id
        response.context.content = content
        response.context.role = ChatRoleType.ASSISTANT
        response.status_detail = content
        response.context.timestamp.GetCurrentTime()

        if serialize is True:
            return response.SerializeToString()
        return response

    async def return_gpt_message(self, event):
        message = event["message"]
        request = Parse(message, ChatRequest())

        # Save Request to Database
        await self.save_request_chat_message(request)

        # Query OpenAI AP
        api_key = await self.get_api_key()
        recent_chat_messages = await self.get_recent_chat_messages(request)

        chatbot = OpenAIAPIWrapper(api_key)

        # Format Recent Chat Messages
        gpt_request_messages = formate_chats_to_gpt_request_messages(
            recent_chat_messages[::-1])

        try:
            gpt_content = chatbot.send(gpt_request_messages)

            # Save GPT Content to Database
            await self.save_gpt_response_message(request, gpt_content)

            # Send Response
            # await self.send(text_data=json.dumps({"message": message}))
            response = self.build_gpt_message_response(request, gpt_content)
        except Exception as error:
            # Handling OpenAIs 500 Internal Server Error
            response = self.build_gpt_message_response(request, str(error))

        await self.send(bytes_data=response)
