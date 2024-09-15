from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt

from ninja import Router, Schema
from ninja.security import django_auth

from bot.models import APIKey


router = Router()
User = get_user_model()


class LoginError(Exception):
    pass


class SignUpError(Exception):
    pass


class LoginIn(Schema):
    username: str
    password: str


class LoginOut(Schema):
    member_id: str
    username: str
    created_at: datetime


class SignUpIn(Schema):
    username: str
    password: str
    email: str


@router.post("/login/", response=LoginOut)
@csrf_exempt
def login(request, data: LoginIn, response: HttpResponse) -> LoginOut:
    if not User.objects.filter(username=data.username).exists():
        raise LoginError("Invalid username")

    user = authenticate(username=data.username, password=data.password)
    if user is None:
        raise LoginError("Invalid password")

    auth_login(request, user)

    response.set_cookie("c_user", user.id, domain=settings.COOKIES_ALLOWED_DOMAIN)

    api_key = APIKey.objects.filter(owner=user).first()
    if api_key:
        response.set_cookie(
            "c_api_key", str(api_key), domain=settings.COOKIES_ALLOWED_DOMAIN
        )

    return LoginOut(
        member_id=str(user.member_id),
        username=user.username,
        created_at=user.date_joined,
    )


@router.get("/logout/", auth=django_auth)
def logout(request, response: HttpResponse):
    if request.user.is_authenticated:
        response.delete_cookie("sessionid", domain=settings.COOKIES_ALLOWED_DOMAIN)
        response.delete_cookie("csrftoken", domain=settings.COOKIES_ALLOWED_DOMAIN)
        response.delete_cookie("c_user", domain=settings.COOKIES_ALLOWED_DOMAIN)
        response.delete_cookie("c_api_key", domain=settings.COOKIES_ALLOWED_DOMAIN)
    return {}


@router.post("/signup/")
@csrf_exempt
def signup(request, data: SignUpIn):
    if User.objects.filter(username=data.username).exists():
        raise SignUpError("Username already exists")

    if User.objects.filter(email=data.email).exists():
        raise SignUpError("Email already exists")

    user = User.objects.create_user(
        username=data.username, email=data.email, password=data.password
    )

    return JsonResponse(
        {"member_id": user.member_id, "username": user.username, "email": user.email}
    )
