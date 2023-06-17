from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token as get_csrf_token

from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import ChatUser, ChatRoom, Chat, PromptTopic, Prompt
from .serializer import ChatUserSerializer, ChatRoomSerializer, ChatSerializer, PromptTopicSerializer, PromptSerializer

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
            session_key = request.session.session_key
            csrf_token = get_csrf_token(request)
            content = {
                "login_status": "success"
            }

            response = JsonResponse(content, safe=False)
            response.set_cookie('sessionid', session_key)
            response.set_cookie('csrftoken', csrf_token)
            return response
        else:
            # Increment the login attempts counter
            # cache.set(username, user_attempts + 1, timeout=600) # Lock the account for 10 minutes
            return HttpResponse('Invalid username or password')


class CustomLogOutView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if self.request.user.is_authenticated:
            response = Response({'detail': 'Successfully logged out'})
            logout(request)
            response.delete_cookie('sessionid')
            response.delete_cookie('csrftoken')
        else:
            response = Response({'detail': 'Logged out failed'})
        return response

class ChatUserAPIView(APIView):
    def get(self, request):
        chat_user = ChatUser.objects.get(user=request.user.id)
        serializer = ChatUserSerializer(chat_user)
        return Response(serializer.data)

class ChatRoomAPIView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all().order_by('-created_at')
    serializer_class = ChatRoomSerializer


class ChatAPIView(generics.ListCreateAPIView):
    queryset = Chat.objects.all().order_by('-created_at')
    serializer_class = ChatSerializer


class ChatHistoryAPIView(APIView):
    def get(self, request, chatroom_id, format=None):
        chats = Chat.objects.filter(chatroom__id=chatroom_id).order_by('-created_at') 
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class PromptTopicAPIView(generics.ListAPIView):
    queryset = PromptTopic.objects.all().order_by('created_at')
    serializer_class = PromptTopicSerializer
    

class PromptAPIView(generics.ListCreateAPIView):
    queryset = Prompt.objects.all().order_by('created_at')
    serializer_class = PromptSerializer