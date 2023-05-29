from rest_framework.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductAll.as_view()),
    path("products/<int:pk>", views.ProductDetail.as_view()),
]
