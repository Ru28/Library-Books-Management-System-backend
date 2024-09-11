from django.urls import path
from .views import Books, RegisterApi, LoginApi, BookDetails, IssueBook, ReturnBook, ListIssuedBooks

urlpatterns = [
    path('',Books.as_view()),
    path('api/register/',RegisterApi.as_view(), name='register'),
    path('api/login/', LoginApi.as_view(), name='login'),
    path('api/books/addbook/', BookDetails.as_view(), name='addbook'),
    path('api/books/remove/<str:book_id>/', BookDetails.as_view(), name='remove_book'),
    path('api/books/issue/', IssueBook.as_view(), name='issue_book'),
    path('api/books/return/', ReturnBook.as_view(), name='return_book'),
    path('api/books/issued/', ListIssuedBooks.as_view(), name='list_issued_books'),
]
