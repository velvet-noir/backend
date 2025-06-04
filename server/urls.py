from django.urls import path
from server import views

urlpatterns = [
    path(r"servers/", views.ServerList.as_view(), name="servers-list"),
    path(r"servers/<int:pk>/", views.ServerDetail.as_view(), name="servers-detail"),
]
