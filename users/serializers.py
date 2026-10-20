# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'age',
                  'can_be_contacted', 'can_data_be_shared']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError(
                "L'inscription nécessite d'avoir au moins 15 ans (RGPD)."
            )
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
