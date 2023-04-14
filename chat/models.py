import uuid

from django.db import models


class ChatRoom(models.Model):
    name = models.CharField(
        unique=True,
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Topic Created Date'
    )

    def __str__(self):
        return self.name

class Chat(models.Model):
    character = models.CharField(max_length=32)

    content = models.TextField()

    tokens = models.IntegerField(default=0)

    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Topic Created Date'
    )

class PromptTopic(models.Model):
    name = models.CharField(
        unique=True,
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Topic Created Date'
    )

    def __str__(self):
        return self.name

class Prompt(models.Model):
    prompt_topic = models.ForeignKey(
        PromptTopic, 
        on_delete=models.CASCADE
    )

    content = models.TextField()

    usage_count = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Topic Created Date'
    )