import uuid
from django.db import models
from django.utils import timezone
from enum import Enum
from bot.models import Bot


class ChatRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ChatRoom(models.Model):
    chatroom_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey("member.Member", on_delete=models.PROTECT)
    name = models.CharField(unique=True, max_length=128)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )

    last_used_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Last Used Time"
    )

    def __str__(self):
        return self.name


class Message(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    role = models.CharField(
        max_length=32, choices=ChatRole.choices(), default=ChatRole.USER.value
    )

    role_id = models.UUIDField(null=True, blank=True, unique=True)

    content = models.TextField()

    tokens = models.IntegerField(default=0)

    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )

    def save(self, *args, **kwargs):
        # Update the last_updated attribute of the related ChatRoom
        self.chatroom.last_used_time = timezone.now()
        self.chatroom.save()

        # Call the original save() method to save the Chat object
        super(Message, self).save(*args, **kwargs)

    def get_role_obj(self):
        if self.role == ChatRole.USER.value:
            return self.chatroom.owner
        else:
            return Bot.objects.get(bot_id=self.role_id)


class PromptTopic(models.Model):
    prompt_topic_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    owner = models.ForeignKey("member.Member", on_delete=models.PROTECT)

    name = models.CharField(unique=True, max_length=128)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )

    def __str__(self):
        return self.name


class Prompt(models.Model):
    prompt_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    prompt_topic = models.ForeignKey(PromptTopic, on_delete=models.CASCADE)

    name = models.CharField(unique=True, max_length=128)

    content = models.TextField()

    usage_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )
