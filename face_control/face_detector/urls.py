from django.conf.urls import url
from .views import detect, simple_upload, fill_base, identity
from django.urls import path, re_path


app_name = 'face_detector'

urlpatterns = [
    path(r'detect/', detect, name="detect"),
    path(r'add_foto/', simple_upload, name="add_foto"),
    path(r'add_to_db/', fill_base, name="add_to_db"),
    re_path(r'(?P<uuid>[a-z\d]{32})/', identity, name="identity"),
]