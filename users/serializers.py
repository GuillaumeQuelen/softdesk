# users/serializers.py
from rest_framework import serializers
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