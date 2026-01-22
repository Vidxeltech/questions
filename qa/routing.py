from django.urls import re_path
from .consumers import ScreenConsumer, ModerationConsumer

websocket_urlpatterns = [
    re_path(r"ws/screen/$", ScreenConsumer.as_asgi()),
    re_path(r"ws/moderation/$", ModerationConsumer.as_asgi()),
]
