from django.urls import include, path

from .views import (
    APIKeyView,
    ChatHistoryAPIView,
    ChatRoomAPIView,
    ChatSocketInitView,
    ChatUserAPIView,
    CustomLogInView,
    CustomLogOutView,
    CustomSignUpView,
    MessageAPIView,
    MessagesAPIView,
    PromptAPIView,
    PromptTopicAPIView,
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("user/", ChatUserAPIView.as_view()),
    path("api-key/", APIKeyView.as_view(), name="api-key"),
    path("chatroom/", ChatRoomAPIView.as_view(), name="chatrooms"),
    path("messages/", MessagesAPIView.as_view(), name="message-list"),
    path("message/<int:pk>/", MessageAPIView.as_view(), name="message-detail"),
    path(
        "chat-history/<int:chatroom_id>/",
        ChatHistoryAPIView.as_view(),
        name="chat-history",
    ),
    path("chat-socket-init/", ChatSocketInitView.as_view()),
    path("prompt-topic/", PromptTopicAPIView.as_view()),
    path("prompts/", PromptAPIView.as_view()),
    path("login/", CustomLogInView.as_view(), name="login"),
    path("logout/", CustomLogOutView.as_view(), name="logout"),
    path("signup/", CustomSignUpView.as_view(), name="signup"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
