from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import RegisterSerializer, UserSerializer, LoginSerializer, BookSerializer
from bson import ObjectId
from datetime import datetime
from db_connection import db
# Create your views here.

class Books(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class RegisterApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username,password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username
                })
            else:
                return Response({'error': 'invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class BookDetails(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book_data = serializer.validated_data
            
            books_collection = db['Books']  
            
            result = books_collection.insert_one(book_data)
            
            return Response(
                {
                    'message': 'Book added successfully',
                    'book_id': str(result.inserted_id) 
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, book_id):
        books_collection = db['Books']
        
        try:
            object_id = ObjectId(book_id)
        except Exception as e:
            return Response({'error': 'Invalid book ID format'}, status=status.HTTP_400_BAD_REQUEST)

        result = books_collection.delete_one({'_id': object_id})

        if result.deleted_count > 0:
            return Response({'message': 'Book removed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

class IssueBook(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')

        books_collection = db['Books']
        book = books_collection.find_one({'_id': ObjectId(book_id)})
        if book:
            if book['book_quantity'] > 0:
                books_collection.update_one(
                    {'_id': book_id},
                    {'$inc': {'book_quantity': -1}}  
                )
                issued_books_collection = db['IssuedBooks']
                issued_books_collection.insert_one({
                    'user_id': user.id,
                    'book_id': book_id,
                    'book_name': book['book_name'],
                    'issued_date': datetime.now()
                })
                return Response({'message': 'Book issued successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


class ReturnBook(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')

        issued_books_collection = db['IssuedBooks']
        issued_book = issued_books_collection.find_one({'user_id': user.id, 'book_id': book_id})
        
        if issued_book:
            issued_books_collection.delete_one({'user_id': user.id, 'book_id': book_id})
            
            books_collection = db['Books']
            books_collection.update_one(
                {'_id': book_id},
                {'$inc': {'book_quantity': +1}}
            )
            return Response({'message': 'Book returned successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Issued book record not found'}, status=status.HTTP_404_NOT_FOUND)


class ListIssuedBooks(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        issued_books_collection = db['IssuedBooks']

        issued_books = issued_books_collection.find({'user_id': user.id})

        issued_books_list = [
            {
                'book_name': book['book_name'],
                'issued_date': book['issued_date'],
                'book_id': book['book_id'],
            }
            for book in issued_books
        ]
        return Response({'issued_books': issued_books_list}, status=status.HTTP_200_OK)