import uuid
from django.db import models


class AIVendor(models.Model):
    name = models.CharField(max_length=64)
    vendor_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class AIModel(models.Model):
    name = models.CharField(max_length=128)
    vendor = models.ForeignKey(AIVendor, on_delete=models.CASCADE)
    model_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

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
