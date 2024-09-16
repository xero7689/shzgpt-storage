from django.contrib import admin

from .models import (
    Modality,
    AIModel,
    AIVendor,
    APIKey,
)


@admin.register(Modality)
class ModalityAdminPage(admin.ModelAdmin):
    list_display = (
        "id",
        "input_type",
        "output_type",
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
    list_display = ["id", "owner", "vendor", "desc", "created_at"]
