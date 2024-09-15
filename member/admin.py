from .models import Member
from django.contrib import admin


# Register your models here.
@admin.register(Member)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "member_id",
        "username",
    ]
