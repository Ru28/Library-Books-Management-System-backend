from django.urls import path
from .views import Books

urlpatterns = [
    path('',Books.as_view()),
]
