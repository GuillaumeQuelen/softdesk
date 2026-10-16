from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly


class ProjectNestedMixin:
    def get_project(self):
        return get_object_or_404(
            Project,
            pk=self.kwargs['project_pk'],
            contributors__user=self.request.user,
        )


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(ProjectNestedMixin, ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Contributor.objects.filter(project=self.get_project())

    def perform_create(self, serializer):
        project = self.get_project()
        if project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut ajouter un contributeur.")
        user = serializer.validated_data['user']
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError({"username": "Cet utilisateur est déjà contributeur du projet."})
        serializer.save(project=project)

    def perform_destroy(self, instance):
        if instance.project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut retirer un contributeur.")
        if instance.user == instance.project.author:
            raise ValidationError("L'auteur ne peut pas être retiré de son propre projet.")
        instance.delete()


class IssueViewSet(ProjectNestedMixin, ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Issue.objects.filter(project=self.get_project())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, project=self.get_project())

class CommentViewSet(ProjectNestedMixin, ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_issue(self):
        return get_object_or_404(
            Issue, pk=self.kwargs['issue_pk'], project=self.get_project()
        )

    def get_queryset(self):
        return Comment.objects.filter(issue=self.get_issue())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, issue=self.get_issue())