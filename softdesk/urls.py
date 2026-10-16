"""
URL configuration for softdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from projects.views import ProjectViewSet, ContributorViewSet, IssueViewSet, CommentViewSet
from users.views import UserViewSet
from projects.views import ProjectViewSet, ContributorViewSet

router = SimpleRouter()
router.register('users', UserViewSet, basename='user')
router.register('projects', ProjectViewSet, basename='project')
router.register(
    r'projects/(?P<project_pk>[^/.]+)/contributors',
    ContributorViewSet,
    basename='project-contributors',
)
router.register(
    r'projects/(?P<project_pk>[^/.]+)/issues',
    IssueViewSet,
    basename='project-issues',
)

router.register(
    r'projects/(?P<project_pk>[^/.]+)/issues/(?P<issue_pk>[^/.]+)/comments',
    CommentViewSet,
    basename='issue-comments',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]