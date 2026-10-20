from rest_framework import serializers
from users.models import User
from .models import Project, Contributor, Issue, Comment


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


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    assigned_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'priority', 'tag', 'status',
                  'author', 'assigned_to', 'created_time']
        read_only_fields = ['id', 'created_time']

    def validate_assigned_to(self, user):
        project = self.context['project']
        if user and not project.contributors.filter(user=user).exists():
            raise serializers.ValidationError(
                "La personne assignée doit être contributrice du projet."
            )
        return user


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'uuid', 'description', 'author', 'created_time']
        read_only_fields = ['id', 'uuid', 'created_time']
