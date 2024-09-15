import logging
from datetime import datetime

import orjson as json
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Chat, ChatRoom
from bot.models import APIKey
from chat.schema import ChatContext, ChatRequest, ChatResponse, ChatRole, ChatStatus
from common.llm_vendor import OpenAILLM
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

    async def receive(self, text_data):
        await login(self.scope, self.scope["user"])

        # Verify the messsage
        json_data = json.loads(text_data)
        request = ChatRequest.model_validate(json_data)

        # Save Request to Database
        await self.save_request_chat_message(request)
        broadcast_response = self.build_brodcast_response(request)

        # Broadcast the request message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group.return.message",
                "return_json": broadcast_response.model_dump_json(),
                "sender_channel_name": self.channel_name,
                "role": ChatRole.USER,
            },
        )

        # Query OpenAI AP
        api_key = await self.get_api_key()
        recent_chat_messages = await self.get_recent_chat_messages(request)

        llm = OpenAILLM(api_key, model="gpt-4o-mini")

        try:
            llm.send(recent_chat_messages[::-1])

            # Save GPT Content to Database
            await self.save_gpt_response_message(
                request, llm.response_content, llm.response_tokens
            )

            response = self.build_gpt_message_response(request, llm.response_content)
        except Exception as error:
            # Handling OpenAIs 500 Internal Server Error
            response = self.build_gpt_message_response(request, str(error))

        # Broadcast the response to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group.return.message",
                "return_json": response.model_dump_json(),
                "sender_channel_name": self.channel_name,
                "role": ChatRole.ASSISTANT,
            },
        )

    async def group_return_message(self, event):
        # Prevent sending message to original sender
        if (
            event["sender_channel_name"] == self.channel_name
            and event["role"] == ChatRole.USER
        ):
            return

        chat_instance = event["return_json"]

        await self.send(text_data=chat_instance)

    @database_sync_to_async
    def get_api_key(self):
        return APIKey.objects.first()

    @database_sync_to_async
    def get_recent_chat_messages(self, request, cal_num=10):
        chatroom_id = request.context.chatroom_id
        recent_messages = (
            Chat.objects.filter(chatroom=chatroom_id)
            .order_by("-created_at")
            .values()[:cal_num]
        )

        # Check token's length
        cur_recents_tokens = sum([message["tokens"] for message in recent_messages])

        while cur_recents_tokens >= 4096:
            removed_msg = recent_messages.pop()
            cur_recents_tokens -= removed_msg.tokens
            logger.debug(f"[get_recent_msg][too_many_tokens][remove] {removed_msg.id}")

        return recent_messages

    @database_sync_to_async
    def save_request_chat_message(self, request):
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        request_message = {
            "role": request.context.role,
            "content": request.context.content,
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

    def build_gpt_message_response(self, request, content):
        context = ChatContext(
            chatroom_id=request.context.chatroom_id,
            role=ChatRole.ASSISTANT,
            content=content,
        )
        response = ChatResponse(
            status=ChatStatus.SUCCESS,
            context=context,
            status_detail="",
            timestamp=int(datetime.now().timestamp()),
        )

        return response

    def build_brodcast_response(self, request):
        context = ChatContext(
            chatroom_id=request.context.chatroom_id,
            role=ChatRole.USER,
            content=request.context.content,
        )
        response = ChatResponse(
            status=ChatStatus.SUCCESS,
            context=context,
            status_detail="",
            timestamp=int(datetime.now().timestamp()),
        )

        return response
