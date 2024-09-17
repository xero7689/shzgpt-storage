from typing import List
import uuid
import datetime
from django.contrib.auth import get_user_model

from ninja import Router, Schema
from ninja.security import django_auth

from bot.models import Bot, AIModel


bot_router = Router()
model_router = Router()

User = get_user_model()


class BotCreateIn(Schema):
    name: str
    desc: str
    model_id: uuid.UUID
    temperature: float
    instruction: str


class AIModelItem(Schema):
    name: str
    vendor_id: uuid.UUID
    model_id: uuid.UUID
    foundation_model_id: str


class BotItem(Schema):
    bot_id: uuid.UUID
    name: str
    desc: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class AIModelNotFound(Exception):
    pass


@model_router.get("/", response=List[AIModelItem], auth=django_auth)
def get_ai_models(request) -> List[AIModelItem]:
    ai_models = AIModel.objects.all()
    ai_model_items = [
        AIModelItem(
            name=ai_model.name,
            vendor_id=ai_model.vendor.vendor_id,
            model_id=ai_model.model_id,
            foundation_model_id=ai_model.foundation_model_id,
        )
        for ai_model in ai_models
    ]
    return ai_model_items


@bot_router.get("/", response=List[BotItem], auth=django_auth)
def get_bots(request) -> List[BotItem]:
    bots = Bot.objects.filter(owner=request.user)
    bot_items = [
        BotItem(
            bot_id=str(bot.bot_id),
            name=bot.name,
            desc=bot.description,
            created_at=bot.created_at,
            updated_at=bot.updated_at,
        )
        for bot in bots
    ]
    return bot_items


@bot_router.post("/", auth=django_auth)
def create_bot(request, data: BotCreateIn):
    try:
        foundation_model = AIModel.objects.get(model_id=data.model_id)
    except AIModel.DoesNotExist:
        raise AIModelNotFound()

    bot = Bot.objects.create(
        owner=request.user,
        name=data.name,
        description=data.desc,
        ai_model=foundation_model,
    )

    return {"bot_id": str(bot.bot_id)}
