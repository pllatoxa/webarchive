from django.urls import path

from .views import (
    MyProjectsView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    project_download,
    ProjectDeleteView,
    ProjectPostCreateView,
    ProjectPostDetailView,
    ProjectPostListView,
    PostCreateView,
    PostListView,
    PostDetailView,
    PostDeleteView,
)

urlpatterns = [
    # Проекты
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/new/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/mine/", MyProjectsView.as_view(), name="my_projects"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    path("projects/<slug:slug>/download/", project_download, name="project_download"),
    path("projects/<slug:slug>/delete/", ProjectDeleteView.as_view(), name="project_delete"),

    # Посты внутри проекта
    path("projects/<slug:slug>/posts/new/", ProjectPostCreateView.as_view(), name="project_post_create"),
    path("projects/posts/<int:pk>/", ProjectPostDetailView.as_view(), name="project_post_detail"),

    # Общие посты
    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/new/", PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
]
