from django.urls import path
from .views import Books, RegisterApi, LoginApi, BookDetails

urlpatterns = [
    path('',Books.as_view()),
    path('api/register/',RegisterApi.as_view(), name='register'),
    path('api/login/', LoginApi.as_view(), name='login'),
    path('api/addbook/', BookDetails.as_view(), name='addbook')
]
