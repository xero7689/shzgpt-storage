from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
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


class Chat(models.Model):
    role = models.CharField(max_length=32)

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
        super(Chat, self).save(*args, **kwargs)


class PromptTopic(models.Model):
    owner = models.ForeignKey("member.Member", on_delete=models.PROTECT)

    name = models.CharField(unique=True, max_length=128)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )

    def __str__(self):
        return self.name


class Prompt(models.Model):
    prompt_topic = models.ForeignKey(PromptTopic, on_delete=models.CASCADE)

    name = models.CharField(unique=True, max_length=128)

    content = models.TextField()

    usage_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )
