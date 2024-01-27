import logging

from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from google.protobuf.json_format import MessageToJson, Parse

from chat.models import APIKey, Chat, ChatRoom
from common.llm_vendor import OpenAILLM
from common.pb.message_pb2 import (ChatRequest, ChatResponse, ChatRoleType,
                                   StatusCode)
from common.tokenizer import num_tokens_from_message

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
            self.room_group_name, {"type": "return.gpt.message", "message": message}
        )

    @database_sync_to_async
    def get_api_key(self):
        return APIKey.objects.first()

    @database_sync_to_async
    def get_recent_chat_messages(self, request, cal_num=10):
        chatroom_id = request.context.chatroom_id

        recent_messages = Chat.objects.filter(chatroom=chatroom_id).order_by(
            '-created_at'
        ).values()[:cal_num]

        # Check token's length
        cur_recents_tokens = sum([message["tokens"] for message in recent_messages])

        while cur_recents_tokens >= 4096:
            removed_msg = recent_messages.pop()
            cur_recents_tokens -= removed_msg.tokens
            logger.debug(f'[get_recent_msg][too_many_tokens][remove] {removed_msg.id}')

        return recent_messages

    @database_sync_to_async
    def save_request_chat_message(self, request):
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        request_message = {
            'role': ChatRoleType.Name(request.context.role).title(),
            'content': request.context.content,
        }
        tokens = num_tokens_from_message(request_message)
        request_chat_message = Chat(
            role="user",
            content=request.context.content,
            chatroom=chatroom,
            tokens=tokens,
        )
        request_chat_message.save()

    @database_sync_to_async
    def save_gpt_response_message(self, request, content: str, tokens: int) -> None:
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        gpt_response_message = Chat(
            role="assistant", content=content, chatroom=chatroom, tokens=tokens
        )
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

        llm = OpenAILLM(api_key)

        try:
            llm.send(recent_chat_messages[::-1])

            # Save GPT Content to Database
            await self.save_gpt_response_message(
                request, llm.response_content, llm.response_tokens
            )

            # Send Response
            response = self.build_gpt_message_response(request, llm.response_content)
        except Exception as error:
            # Handling OpenAIs 500 Internal Server Error
            response = self.build_gpt_message_response(request, str(error))

        await self.send(bytes_data=response)
