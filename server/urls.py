from django.urls import path

from server import views

urlpatterns = [
    path("hello/", views.hello),
]
