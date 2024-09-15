from rest_framework import serializers

from .models import Chat, ChatRoom, Prompt, PromptTopic


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "role", "content", "chatroom", "tokens", "created_at"]


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ["id", "name", "created_at", "last_used_time"]


class PromptTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTopic
        fields = ["id", "name"]


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ["id", "prompt_topic", "name", "content"]
