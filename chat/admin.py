from django.contrib import admin

from .models import ChatUser, ChatRoom, Chat, PromptTopic, Prompt

# Register your models here.

@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'created_at',
    ]

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'owner',
        'name',
        'created_at',
        'last_used_time',
    ]


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'created_at',
        'chatroom',
        'role',
        'tokens',
        'content'
    ]


@admin.register(PromptTopic)
class PromptTopicAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'created_at'
    ]


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prompt_topic',
        'usage_count',
        'content',
        'created_at'
    ]