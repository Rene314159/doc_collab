from django.urls import re_path
from doc_collab_app.consumers import DocumentConsumer

websocket_urlpatterns = [
    re_path(r"^ws/document/(?P<document_id>[^/]+)/$", DocumentConsumer.as_asgi()),
]
