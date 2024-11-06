from django.urls import path, re_path
from server1.views import test, request_process

urlpatterns = [
#    path('test', test, name = "test"),
    re_path(r'^.*$', request_process, name = "request process"),
]
