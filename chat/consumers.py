import logging
from datetime import datetime
import asyncio

import orjson as json
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from shz_llm_client import OpenAIClient, RequestMessage
import openai
from pydantic import BaseModel

from bot.models import APIKey
from chat.models import ChatRoom, Message
from chat.schema import ChatContext, ChatRequest, ChatResponse, ChatRole, ChatStatus
from common.tokenizer import num_tokens_from_message
from libs.crawler import fetch_website, parse_website_metadata

logger = logging.getLogger(__name__)


class URLExtractor(BaseModel):
    urls: list[str]


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

        # Query OpenAI API
        api_key = await self.get_api_key()
        recent_chat_messages = await self.get_recent_chat_messages(request)
        system_prompt = RequestMessage(
            role="system", content="You are a helpful assistant."
        )

        # Chat Client
        client = OpenAIClient(api_key, model_id="gpt-4o-mini", stream=False)

        # Parse URL from the message
        possible_urls = await self.parse_url_from_context(request.context.content)

        # Use async gather to fetch multiple websites concurrently
        if possible_urls:
            tasks = [fetch_website(url) for url in possible_urls]
            website_contents = await asyncio.gather(*tasks)

            # Parse the website metadata
            metadata = {
                url: parse_website_metadata(content)
                for url, content in website_contents
            }

            print(metadata)

            addtional_url_context = "\n".join(
                [
                    f"URL: {url}\nTitle: {data['title']}\nSubtitle: {data['subtitle']}\nText: {data['text']}"
                    for url, data in metadata.items()
                ]
            )

            system_prompt.content += f"\n\nYou are going to answer user's question based on following addtional URL context:\n\n{addtional_url_context}"

        messages = []
        for message in recent_chat_messages[::-1]:
            messages.append(
                RequestMessage(role=message["role"], content=message["content"])
            )

        try:
            response = client.send(messages, system_prompt)

            # Save GPT Content to Database
            await self.save_gpt_response_message(request, response, 0)

            response = self.build_gpt_message_response(request, response)
        except Exception as error:
            logger.error(f"Query LLM Error: {error}")
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
            Message.objects.filter(chatroom=chatroom_id)
            .order_by("-created_at")
            .values()[:cal_num]
        )

        # Check token's length
        messages = [message for message in recent_messages]
        cur_recents_tokens = sum([message["tokens"] for message in messages])

        while cur_recents_tokens >= 4096:
            removed_msg = messages.pop()
            cur_recents_tokens -= removed_msg["tokens"]
            logger.debug(
                f"[get_recent_msg][too_many_tokens][remove] {removed_msg['id']}"
            )

        return messages

    @database_sync_to_async
    def save_request_chat_message(self, request):
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        request_message = {
            "role": request.context.role,
            "content": request.context.content,
        }
        tokens = num_tokens_from_message(request_message)
        request_chat_message = Message(
            role="user",
            content=request.context.content,
            chatroom=chatroom,
            tokens=tokens,
        )
        request_chat_message.save()

    @database_sync_to_async
    def save_gpt_response_message(self, request, content: str, tokens: int) -> None:
        chatroom = ChatRoom.objects.get(id=request.context.chatroom_id)
        gpt_response_message = Message(
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

    async def parse_url_from_context(self, context) -> list[str]:
        # Helper Client for structured output
        api_key = await self.get_api_key()
        helper_client = openai.OpenAI(api_key=api_key)

        # Try to fetch and parse website if user's message contains URL
        completion = helper_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful URL extractor, you can extract URLs from text.",
                },
                {"role": "user", "content": context},
            ],
            response_format=URLExtractor,
        )

        message = completion.choices[0].message
        if message.parsed:
            return message.parsed.urls
