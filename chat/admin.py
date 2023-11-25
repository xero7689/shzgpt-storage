from django.contrib import admin
from django.db.models import Count

from .models import (
    ChatUser,
    ChatRoom,
    Chat,
    PromptTopic,
    Prompt,
    APIKey,
    AIVendor,
    AIModel,
)

# Register your models here.


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'created_at',
    ]


@admin.register(AIVendor)
class AIVendor(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(AIModel)
class AIModel(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'vendor',
    ]


@admin.register(APIKey)
class APIKey(admin.ModelAdmin):
    list_display = ['id', 'owner', 'model', 'desc', 'created_at']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'owner',
        'name',
        'chat_count',
        'created_at',
        'last_used_time',
    ]

    # Override default queryset
    # Annotate Chat Count to it
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(chat_count=Count('chat'))
        return queryset

    def chat_count(self, obj):
        return obj.chat_count

    chat_count.admin_order_field = 'chat_count'
    chat_count.short_description = 'Chats'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'chatroom', 'role', 'tokens', 'content']


@admin.register(PromptTopic)
class PromptTopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'created_at']


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt_topic', 'usage_count', 'content', 'created_at']
