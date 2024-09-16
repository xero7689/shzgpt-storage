import uuid
from django.db import models


class Modality(models.Model):
    class ModalityType(models.TextChoices):
        IMAGE = "IMAGE"
        VIDEO = "VIDEO"
        AUDIO = "AUDIO"
        TEXT = "TEXT"

    input_type = models.CharField(
        max_length=32, choices=ModalityType.choices, default=ModalityType.TEXT
    )

    output_type = models.CharField(
        max_length=32, choices=ModalityType.choices, default=ModalityType.TEXT
    )

    class Meta:
        verbose_name = "Modality"
        verbose_name_plural = "Modalities"

    def __str__(self) -> str:
        return f"{self.input_type} to {self.output_type}"


class AIVendor(models.Model):
    name = models.CharField(max_length=64)
    vendor_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AIModel(models.Model):
    name = models.CharField(max_length=128)
    vendor = models.ForeignKey(AIVendor, on_delete=models.CASCADE)
    model_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    foundation_model_id = models.CharField(max_length=255)

    modalities = models.ManyToManyField(
        "bot.Modality",
        related_name="ai_models",
        related_query_name="ai_model",
    )

    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class APIKey(models.Model):
    owner = models.ForeignKey("member.Member", on_delete=models.CASCADE)
    key = models.CharField(max_length=256)
    desc = models.CharField(max_length=256, blank=True)
    vendor = models.ForeignKey(AIVendor, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Topic Created Date"
    )

    def __str__(self):
        return self.key
