from django.contrib import admin

from .models import (
    AIModel,
    AIVendor,
    APIKey,
)


@admin.register(AIVendor)
class AIVendor(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(AIModel)
class AIModel(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "vendor",
    ]


@admin.register(APIKey)
class APIKey(admin.ModelAdmin):
    list_display = ["id", "owner", "model", "desc", "created_at"]
