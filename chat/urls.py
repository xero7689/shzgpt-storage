from django.urls import include, path
from .views import ChatRoomAPIView, ChatAPIView, ChatHistoryAPIView, PromptTopicAPIView, PromptAPIView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('chatroom/', ChatRoomAPIView.as_view()),
    path('chat/', ChatAPIView.as_view()),
    path('chat-history/<int:chatroom_id>/', ChatHistoryAPIView.as_view()),
    path('prompt-topic/', PromptTopicAPIView.as_view()),
    path('prompts/', PromptAPIView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]