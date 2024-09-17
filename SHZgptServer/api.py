import orjson
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer

from member.api import router as member_router
from member.api import LoginError, SignUpError
from bot.api import bot_router, model_router, AIModelNotFound
from chat.api import chatroom_router


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


api = NinjaAPI(csrf=True, renderer=ORJSONRenderer())


@api.exception_handler(LoginError)
def login_error(request, exc):
    return api.create_response(
        request,
        {"message": "Invalid username or password"},
        status=401,
    )


@api.exception_handler(SignUpError)
def signup_error(request, exc):
    return api.create_response(
        request,
        {"message": "Username or email already exists"},
        status=409,
    )


@api.exception_handler(AIModelNotFound)
def ai_model_not_found(request, exc):
    return api.create_response(request, {"message": "AI Model not found"}, status=404)


api.add_router("/members", member_router)
api.add_router("/models", model_router)
api.add_router("/bots", bot_router)
api.add_router("/chatrooms", chatroom_router)
