from django.urls import include, path
from .views import CustomLogInView, CustomLogOutView, ChatUserAPIView, ChatRoomAPIView, ChatAPIView, ChatHistoryAPIView, PromptTopicAPIView, PromptAPIView, APIKeyView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('user/', ChatUserAPIView.as_view()),
    path('api-key/', APIKeyView.as_view()),
    path('chatroom/', ChatRoomAPIView.as_view(), name='chatrooms'),
    path('chat/', ChatAPIView.as_view()),
    path('chat-history/<int:chatroom_id>/', ChatHistoryAPIView.as_view(), name='chat-history'),
    path('prompt-topic/', PromptTopicAPIView.as_view()),
    path('prompts/', PromptAPIView.as_view()),
    path('login/', CustomLogInView.as_view(), name='login'),
    path('logout/', CustomLogOutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
