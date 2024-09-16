from rest_framework import serializers

from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["id", "key", "desc", "model", "created_at"]
