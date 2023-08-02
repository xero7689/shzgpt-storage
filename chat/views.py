from datetime import datetime

from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.core.cache import cache

from django.http import HttpResponse, JsonResponse

from django.conf import settings

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status

from .models import ChatUser, ChatRoom, Chat, PromptTopic, Prompt, APIKey
from .serializer import ChatUserSerializer, ChatRoomSerializer, ChatSerializer, PromptTopicSerializer, PromptSerializer, APIKeySerializer


class CustomLogInView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if this user has exceeded the maximum login attempts
        # user_attempts = cache.get(username, 0)
        # if user_attempts >= 5:
        # return HttpResponse('Account locked due to too many login attempts')

        if not username:
            return HttpResponse('Username is required')

        if not password:
            return HttpResponse('Password is required')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset the login attempts counter
            # cache.delete(username)
            login(request, user)

            chatUser = ChatUser.objects.get(user=user)

            serializer = ChatUserSerializer(chatUser)
            content = {
                'data': serializer.data,
                'status': 'success'
            }

            response = JsonResponse(content, safe=False)
            response.set_cookie('c_user', chatUser.id,
                                domain=settings.COOKIES_ALLOWED_DOMAIN)

            openai_api_key = APIKey.objects.filter(owner__user=user).first()
            if openai_api_key:
                response.set_cookie('c_api_key', openai_api_key,
                                    domain=settings.COOKIES_ALLOWED_DOMAIN)

            return response
        else:
            # Increment the login attempts counter
            # cache.set(username, user_attempts + 1, timeout=600) # Lock the account for 10 minutes
            content = {
                'status': 'failed',
                'detail': 'Invalid username or password'
            }
            return JsonResponse(content, status=status.HTTP_401_UNAUTHORIZED)


class CustomLogOutView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if self.request.user.is_authenticated:
            response = Response({
                'status': 'success',
                'detail': 'Successfully logged out'
            })
            response.delete_cookie(
                'sessionid', domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie(
                'csrftoken', domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie(
                'c_user', domain=settings.COOKIES_ALLOWED_DOMAIN)
            response.delete_cookie(
                'c_api_key', domain=settings.COOKIES_ALLOWED_DOMAIN)
        else:
            response = Response({
                'status': 'failed',
                'detail': 'Logged out failed'
            })
        return response


class ChatUserAPIView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chat_user = ChatUser.objects.get(user=request.user.id)
        serializer = ChatUserSerializer(chat_user)
        return Response(serializer.data)


class ChatRoomAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        queryset_cache_key = f'views.queryset.cache.chatroomapi.{user}'
        cached_queryset = cache.get(queryset_cache_key)

        if cached_queryset is not None:
            queryset = cached_queryset
        else:
            queryset = ChatRoom.objects.filter(
                owner__user=user).order_by('created_at')
            cache.set(queryset_cache_key, queryset, 60 * 60)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=ChatUser.objects.get(user=self.request.user))

        user = self.request.user
        queryset_cache_key = f'views.queryset.cache.chatroomapi.{user}'
        queryset = ChatRoom.objects.filter(
            owner__user=user).order_by('created_at')
        cache.set(queryset_cache_key, queryset, 60 * 60)


class ChatAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Chat.objects.all().order_by('-created_at')
    serializer_class = ChatSerializer


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

        chatroom = ChatRoom.objects.filter(
            owner__user=user, id=chatroom_id).first()
        if not chatroom:
            return Response({
                'status': 'failed',
                'detail': 'Invalid Chatroom ID',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the date_gte and date_lt parameters from the GET query
        date_gte_str = request.GET.get('date_gte')
        date_lt_str = request.GET.get('date_lt')

        # Set default start and end dates if not provided
        chats = Chat.objects.filter(chatroom=chatroom).order_by('created_at')
        if not chats.exists():
            return Response({
                'status': 'failed',
                'detail': 'No chat history for the specified chatroom',
            }, status=status.HTTP_404_NOT_FOUND)

        start_date = chats.first().created_at
        end_date = timezone.now()

        # Parse datetime strings to objects and update start/end date accordingly
        try:
            if date_gte_str:
                start_date = datetime.strptime(
                    date_gte_str, '%Y-%m-%d %H:%M:%S')
            if date_lt_str:
                end_date = datetime.strptime(date_lt_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as ve:
            return Response({
                'status': 'failed',
                'detail': str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)

        # If both start and end dates are the same, add 1 second to end_date to include messages during that second
        if start_date == end_date:
            end_date += timezone.timedelta(seconds=1)

        # Fetch chats based on start and end dates
        chats = Chat.objects.filter(
            chatroom=chatroom,
            created_at__gte=start_date,
            created_at__lt=end_date
        ).order_by('-created_at')

        # If date_gte or date_lt is not provided, limit number of results to DEFAULT_CHAT_LIMIT
        if not date_gte_str and not date_lt_str:
            chats = chats[:self.DEFAULT_CHAT_LIMIT]

        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class PromptTopicAPIView(generics.ListAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = PromptTopic.objects.all().order_by('created_at')
    serializer_class = PromptTopicSerializer


class PromptAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Prompt.objects.all().order_by('created_at')
    serializer_class = PromptSerializer


class APIKeyView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = APIKeySerializer

    def get_queryset(self):
        user = self.request.user
        return APIKey.objects.filter(owner__user=user).order_by('created_at')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        owner = ChatUser.objects.get(user=self.request.user)
        api_key = serializer.save(owner=owner)
        return Response(self.serializer_class(api_key).data, status=status.HTTP_201_CREATED)
