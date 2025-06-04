from django.urls import path

from server import views

urlpatterns = [
    path("", views.GetOrders),
    path("order/<int:id>/", views.GetOrder, name="order_url"),
]
