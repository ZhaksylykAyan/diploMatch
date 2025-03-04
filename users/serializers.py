from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom JWT serializer to include role and profile status """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['is_profile_completed'] = user.is_profile_completed
        return token

class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Serializer for user registration with password confirmation """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True,style={'input_type': 'password'} )

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'confirm_password')

    def validate(self, data):
        """ Validate that passwords match """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """ Assign user role automatically and create user """
        validated_data.pop('confirm_password')  # Remove confirm_password before saving
        email = validated_data['email']
        if '_' in email:
            validated_data['role'] = 'student'
        elif '.' in email:
            validated_data['role'] = 'supervisor'

        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for user details """
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'is_profile_completed')