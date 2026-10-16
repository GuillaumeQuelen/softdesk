from django.conf import settings
from django.db import models
import uuid

class Project(models.Model):
    TYPES = [
        ('BACKEND', 'Back-end'),
        ('FRONTEND', 'Front-end'),
        ('IOS', 'iOS'),
        ('ANDROID', 'Android'),
    ]

    title = models.CharField(max_length=128)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TYPES)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
    )
    created_time = models.DateTimeField(auto_now_add=True)

class Contributor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='contributors')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'],
                                    name='unique_contributor')
        ]

class Issue(models.Model):
    PRIORITIES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    TAGS = [('BUG', 'Bug'), ('FEATURE', 'Feature'), ('TASK', 'Task')]
    STATUSES = [('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished')]

    title = models.CharField(max_length=128)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITIES)
    tag = models.CharField(max_length=7, choices=TAGS)
    status = models.CharField(max_length=11, choices=STATUSES, default='TODO')
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='issues')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='issues_authored')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='issues_assigned')
    created_time = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    description = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE,
                              related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)