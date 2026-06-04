from django.urls import re_path
from .consumers import SubmissionConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/task/(?P<task_id>\d+)/$",
        SubmissionConsumer.as_asgi(),
    ),
]