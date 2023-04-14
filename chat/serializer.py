from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import ChatRoom, Chat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'character', 'content', 'chatroom', 'tokens', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at']
