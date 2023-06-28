from django.contrib import admin

from .models import ChatUser, ChatRoom, Chat, PromptTopic, Prompt, APIKey, AIVendor, AIModel

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
    list_display = [
        'id',
        'name'
    ]


@admin.register(AIModel)
class AIModel(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'vendor',
    ]


@admin.register(APIKey)
class APIKey(admin.ModelAdmin):
    list_display = [
        'id',
        'owner',
        'model',
        'desc',
        'created_at'
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
        'owner',
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
