from django.urls import include, path
from server import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet, basename="user")

urlpatterns = [
    path(r"servers/", views.ServerList.as_view(), name="servers-list"),
    path(r"servers/<int:pk>/", views.ServerDetail.as_view(), name="servers-detail"),
    path(r"servers/spec/", views.ServerSpecList.as_view(), name="servers-spec-list"),
    path(
        r"servers/spec/<int:pk>/",
        views.ServerSpecDetail.as_view(),
        name="servers-spec-detail",
    ),
    path(r"app/", views.ApplicationList.as_view(), name="application-list"),
    path(
        r"app/<int:pk>/",
        views.ApplicationDetail.as_view(),
        name="application-detail",
    ),
    path(
        "app/<int:pk>/formed/",
        views.ApplicationFormed.as_view(),
        name="application-formed",
    ),
    path(
        r"app/<int:app_id>/del/<int:server_id>",
        views.ApplicationDeleteServer.as_view(),
        name="remove-service-from-applic",
    ),
    path("", include(router.urls)),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
