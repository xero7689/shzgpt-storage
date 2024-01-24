from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (APIKeyView, ChatAPIView, ChatHistoryAPIView,
                    ChatRoomAPIView, ChatsAPIView, ChatSocketInitView,
                    ChatUserAPIView, CustomLogInView, CustomLogOutView,
                    PromptAPIView, PromptTopicAPIView)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('user/', ChatUserAPIView.as_view()),
    path('api-key/', APIKeyView.as_view(), name='api-key'),
    path('chatroom/', ChatRoomAPIView.as_view(), name='chatrooms'),
    path('chats/', ChatsAPIView.as_view(), name='chat-list'),
    path('chat/<int:pk>/', ChatAPIView.as_view(), name='chat-detail'),
    path(
        'chat-history/<int:chatroom_id>/',
        ChatHistoryAPIView.as_view(),
        name='chat-history',
    ),
    path('chat-socket-init/', ChatSocketInitView.as_view()),
    path('prompt-topic/', PromptTopicAPIView.as_view()),
    path('prompts/', PromptAPIView.as_view()),
    path('login/', CustomLogInView.as_view(), name='login'),
    path('logout/', CustomLogOutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
