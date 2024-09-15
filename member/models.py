from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class Member(AbstractUser):
    member_id = models.UUIDField(unique=True, default=uuid4, editable=False)
