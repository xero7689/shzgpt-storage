import orjson
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer

from member.api import router as member_router
from member.api import LoginError, SignUpError


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


api.add_router("/members", member_router)
