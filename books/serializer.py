from rest_framework import serializers
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }
        
    def create(self,validated_data):
        user = User.objects.create_user(username=validated_data['username'] ,email = validated_data['email'],password = validated_data['password'])
        return user
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class BookSerializer(serializers.Serializer):
    book_name = serializers.CharField(max_length=100)
    book_title = serializers.CharField(max_length=100)
    book_author = serializers.CharField(max_length=100)
    book_description = serializers.CharField(max_length=500)
    book_pages = serializers.IntegerField()