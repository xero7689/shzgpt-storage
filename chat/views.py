from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token as get_csrf_token

from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status

from .models import ChatUser, ChatRoom, Chat, PromptTopic, Prompt, APIKey
from .serializer import ChatUserSerializer, ChatRoomSerializer, ChatSerializer, PromptTopicSerializer, PromptSerializer, APIKeySerializer
from .permissions import IsSuperUser
from .paginators import ChatHistoryPagination


def print_session(request):
    print('---')
    for k, v in request.session.items():
        print('{} => {}'.format(k, v))


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
            session_key = request.session.session_key
            csrf_token = get_csrf_token(request)

            response = JsonResponse(content, safe=False)
            response.set_cookie('sessionid', session_key)
            response.set_cookie('csrftoken', csrf_token)
            response.set_cookie('c_user', chatUser.id)
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
            logout(request)
            response.delete_cookie('sessionid')
            response.delete_cookie('csrftoken')
            response.delete_cookie('c_user')
            response.delete_cookie('c_api_key')
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
        return ChatRoom.objects.filter(owner__user=user).order_by('created_at')


class ChatAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Chat.objects.all().order_by('-created_at')
    serializer_class = ChatSerializer


class ChatHistoryAPIView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ChatHistoryPagination

    def __init__(self, *args, **kwargs):
        super(ChatHistoryAPIView, self).__init__(*args, **kwargs)
        self.paginator = self.pagination_class()

    def get(self, request, chatroom_id, format=None):
        user = request.user
        chats = Chat.objects.filter(chatroom__owner__user=user).filter(
            chatroom__id=chatroom_id).order_by('-created_at')

        # page = self.paginate_queryset(chats)
        page = self.paginator.paginate_queryset(chats, self.request)

        if page is not None:
            serializer = ChatSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)

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
