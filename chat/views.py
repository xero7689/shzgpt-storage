from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response

from .models import ChatRoom, Chat
from .serializer import ChatRoomSerializer, ChatSerializer


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