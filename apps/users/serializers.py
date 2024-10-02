import re
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers
from apps.users.models import CustomUser
import random
from django.utils import timezone
User = get_user_model()


class OTPChoiceTypeSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    email = serializers.EmailField(required=False, default="NULL")
    phone = serializers.CharField(required=False, default="NULL")

    def validate(self, data):
        errors = {}
        if data.get('email') == "NULL" and data.get('phone') == "NULL":
            errors['phone'] = "Phone or email must be provided."
        if errors:
            raise serializers.ValidationError(errors)
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Dynamically reference the user model
        fields = ['first_name','last_name']  # Only include full_name for updates

    def validate_full_name(self, value):
        # You can add any validation for full_name if necessary
        return value
