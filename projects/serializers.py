from rest_framework import serializers
from .models import Project
from users.models import User
from .models import Project, Contributor


class ContributorSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        source='user',
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Contributor
        fields = ['id', 'username', 'created_time']
        read_only_fields = ['id', 'created_time']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']