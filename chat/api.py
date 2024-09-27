import datetime
import uuid
from typing import List

from django.contrib.auth import get_user_model
from ninja import Router, Schema
from ninja.security import django_auth

from chat.models import ChatRoom

chatroom_router = Router()
message_router = Router()

User = get_user_model()


class ChatRoomItem(Schema):
    chatroom_id: uuid.UUID
    name: str
    created_at: datetime.datetime
    last_used_time: datetime.datetime


class ChatRoomCreateIn(Schema):
    name: str


class ChatRoomNotFound(Exception):
    pass


@chatroom_router.get("/", response=List[ChatRoomItem], auth=django_auth)
def get_chatrooms(request):
    chatrooms = ChatRoom.objects.filter(owner=request.user).order_by("created_at")

    chatroom_items = [
        ChatRoomItem(
            chatroom_id=chatroom.chatroom_id,
            name=chatroom.name,
            created_at=chatroom.created_at,
            last_used_time=chatroom.last_used_time,
        )
        for chatroom in chatrooms
    ]
    return chatroom_items


@chatroom_router.post("/", response=ChatRoomItem, auth=django_auth)
def create_chatroom(request, data: ChatRoomCreateIn):
    chatroom = ChatRoom.objects.create(owner=request.user, name=data.name)

    return ChatRoomItem(
        chatroom_id=chatroom.chatroom_id,
        name=chatroom.name,
        created_at=chatroom.created_at,
        last_used_time=chatroom.last_used_time,
    )


@chatroom_router.put("/{chatroom_id}/", response=ChatRoomItem, auth=django_auth)
def update_chatroom(request, data: ChatRoomCreateIn, chatroom_id: uuid.UUID):
    try:
        chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
    except ChatRoom.DoesNotExist:
        raise ChatRoomNotFound()

    chatroom.name = data.name
    chatroom.save()

    return ChatRoomItem(
        chatroom_id=chatroom.chatroom_id,
        name=chatroom.name,
        created_at=chatroom.created_at,
        last_used_time=chatroom.last_used_time,
    )


@chatroom_router.delete("/{chatroom_id}/", auth=django_auth)
def delete_chatroom(request, chatroom_id: uuid.UUID):
    try:
        chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
    except ChatRoom.DoesNotExist:
        raise ChatRoomNotFound()

    chatroom.delete()

    return {"message": "Chatroom deleted"}
