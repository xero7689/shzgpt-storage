import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import authentication, generics, permissions, status
from rest_framework.response import Response
from rest_framework.serializers import ReturnDict
from rest_framework.views import APIView

from bot.models import APIKey
from bot.serializers import APIKeySerializer
from member.serializers import MemberSerializer

from .models import ChatRoom, Message, Prompt, PromptTopic
from .serializers import (
    ChatRoomSerializer,
    MessageSerializer,
    PromptSerializer,
    PromptTopicSerializer,
)
from .utils import build_response_content, mask_api_key

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomLogInView(APIView):
    def post(self, request, *args, **kwargs) -> JsonResponse:
        username: str = request.data.get("username")
        password: str = request.data.get("password")

        if not username or not password:
            content = build_response_content(
                data=ReturnDict(serializer=MemberSerializer),
                status="failed",
                detail="Username/Password is required",
            )
            return JsonResponse(
                content, status=status.HTTP_401_UNAUTHORIZED, safe=False
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Todo:
            # We should Make ChatUser directly as The AbstractUser
            # Then we dont need to query the ChatUser again
            # after authenticate the user
            serializer = MemberSerializer(user)
            content = build_response_content(
                data=serializer.data, status="succeeded", detail=""
            )

            response = JsonResponse(content, safe=False)
            response.set_cookie(
                "c_user", user.id, domain=settings.COOKIES_ALLOWED_DOMAIN
            )

            api_key = APIKey.objects.filter(owner=user).first()
            if api_key:
                masked_key = mask_api_key(api_key.key)
                response.set_cookie(
                    "c_api_key", str(masked_key), domain=settings.COOKIES_ALLOWED_DOMAIN
                )

            return response
        else:
            content = build_response_content(
                data=ReturnDict(serializer=MemberSerializer),
                status="failed",
                detail="Username/Password Invalid",
            )
            return JsonResponse(content, status=status.HTTP_401_UNAUTHORIZED)


class CustomLogOutView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if self.request.user.is_authenticated:
            response = Response(
                {"status": "succeeded", "detail": "Successfully logged out"}
            )
            response.delete_cookie("sessionid", domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie("csrftoken", domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie("c_user", domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie("c_api_key", domain=settings.COOKIES_ALLOWED_DOMAIN)
        else:
            response = Response({"status": "failed", "detail": "Logged out failed"})
        return response


class CustomSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        username: str = request.data.get("username")
        password: str = request.data.get("password")
        email: str = request.data.get("email")

        if not username or not password or not email:
            content = build_response_content(
                data=ReturnDict(serializer=MemberSerializer),
                status="failed",
                detail="Username/Password/Email is required",
            )
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST, safe=False)

        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        if user is not None:
            login(request, user)
            return Response({"status": "succeeded", "detail": "Successfully signed up"})

        return Response(
            {"status": "failed", "detail": "Failed to sign up"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ChatUserAPIView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = MemberSerializer(request.user)
        return Response(serializer.data)


class ChatRoomAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        queryset_cache_key = f"views.queryset.cache.chatroomapi.{user}"
        cached_queryset = cache.get(queryset_cache_key)

        if cached_queryset is not None:
            queryset = cached_queryset
        else:
            queryset = ChatRoom.objects.filter(owner=user).order_by("created_at")
            cache.set(queryset_cache_key, queryset, 60 * 60)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        user = self.request.user
        queryset_cache_key = f"views.queryset.cache.chatroomapi.{user}"
        queryset = ChatRoom.objects.filter(owner=user).order_by("created_at")
        cache.set(queryset_cache_key, queryset, 60 * 60)


class MessagesAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.all().order_by("-created_at")
    serializer_class = MessageSerializer


class MessageAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class ChatHistoryAPIView(APIView):
    """
    View to retrieve the chat history for a particular chatroom, with optional datetime filters.

    If the `date_gte` and `date_lt` parameters are not provided in the GET request, this view will return
    the latest 20 chat messages for the given `chatroom_id`.

    If the `date_gte` and/or `date_lt` parameters are provided, this view will return all chat messages that
    were created between the given range of datetimes, for the given `chatroom_id`.

    Accepted query parameters:
    - date_gte (optional): Filter the chat messages to only include those created on or after this datetime.
      Format: %Y-%m-%d %H:%M:%S (e.g. "2021-09-01 09:30:00").
    - date_lt (optional): Filter the chat messages to only include those created before this datetime.
      Format: %Y-%m-%d %H:%M:%S (e.g. "2021-10-01 18:15:00").

    Returns a JSON response containing an array of `ChatSerializer`-serialized data.
    """

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    DEFAULT_CHAT_LIMIT = 20

    def __init__(self, *args, **kwargs):
        super(ChatHistoryAPIView, self).__init__(*args, **kwargs)

    # @method_decorator(cache_page(60*60*2))
    def get(self, request, chatroom_id, format=None):
        """
        Retrieves the chat history for the given chatroom ID, with optional datetime filters.

        :param request: The `Request` object passed by the Django server.
        :param chatroom_id: The ID of the chatroom to retrieve the chat history for.
        :param format: The content type format of the response (e.g. "json", "html").
        :returns: A `Response` object containing the serialized chat history data.
        """

        user = request.user

        chatroom = ChatRoom.objects.filter(owner=user, id=chatroom_id).first()
        if not chatroom:
            return Response(
                {
                    "status": "failed",
                    "detail": "Invalid Chatroom ID",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the date_gte and date_lt parameters from the GET query
        date_gte_str = request.GET.get("date_gte")
        date_lt_str = request.GET.get("date_lt")

        # Set default start and end dates if not provided
        chats = Message.objects.filter(chatroom=chatroom).order_by("created_at")
        if not chats.exists():
            return Response(
                {
                    "status": "failed",
                    "detail": "No chat history for the specified chatroom",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        start_date = chats.first().created_at
        end_date = timezone.now()

        # Parse datetime strings to objects and update start/end date accordingly
        try:
            if date_gte_str:
                start_date = datetime.strptime(date_gte_str, "%Y-%m-%d %H:%M:%S")
            if date_lt_str:
                end_date = datetime.strptime(date_lt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            return Response(
                {"status": "failed", "detail": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If both start and end dates are the same, add 1 second to end_date to include messages during that second
        if start_date == end_date:
            end_date += timezone.timedelta(seconds=1)

        # Fetch chats based on start and end dates
        chats = Message.objects.filter(
            chatroom=chatroom, created_at__gte=start_date, created_at__lt=end_date
        ).order_by("-created_at")

        # If date_gte or date_lt is not provided, limit number of results to DEFAULT_CHAT_LIMIT
        if not date_gte_str and not date_lt_str:
            chats = chats[: self.DEFAULT_CHAT_LIMIT]

        serializer = MessageSerializer(chats, many=True)
        return Response(serializer.data)


class PromptTopicAPIView(generics.ListAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = PromptTopic.objects.all().order_by("created_at")
    serializer_class = PromptTopicSerializer


class PromptAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Prompt.objects.all().order_by("created_at")
    serializer_class = PromptSerializer


class APIKeyView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = APIKeySerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        api_keys = APIKey.objects.filter(owner=user).order_by("created_at")
        masked_api_keys = []

        for api_key in api_keys:
            masked_key = mask_api_key(api_key.key)
            masked_api_keys.append(masked_key)

        # Modify the response as per your requirement
        response_data = {
            "masked_api_keys": masked_api_keys,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.save(owner=self.request.user)
        return Response(
            self.serializer_class(api_key).data, status=status.HTTP_201_CREATED
        )


class ChatSocketInitView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chat_socket_init_state = {
            "chatroomId": None,
            "content": None,
            "role": None,
            "timestamp": None,
        }
        return JsonResponse(chat_socket_init_state)
