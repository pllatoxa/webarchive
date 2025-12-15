# archive/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledAuthenticationForm

urlpatterns = [
    # Главная
    path("", views.HomePageView.as_view(), name="home"),

    # Лента постов / обсуждений (оставляем только feed; сами проекты отдаются через hub)
    path("projects/feed/", views.ProjectFeedView.as_view(), name="project_feed"),

    # Посты
    path("posts/new/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/like/", views.post_like, name="post_like"),
    path("posts/<int:pk>/dislike/", views.post_dislike, name="post_dislike"),

    # Вход по почте (код)
    path("auth/email/", views.email_login_request, name="email_login_request"),
    path("auth/email/verify/", views.email_login_verify, name="email_login_verify"),

    # Логин / логаут
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="archive/login.html",
            authentication_form=StyledAuthenticationForm,
        ),
        name="login",
    ),

    # Профиль
    path("profile/", views.profile_view, name="profile"),

    # Донаты
    path("donate/", views.DonateView.as_view(), name="donate"),

    # Каталог / категории / подборки — оставлены для совместимости,
    # но можно скрывать в интерфейсе.
    path("resources/", views.ResourceListView.as_view(), name="resource_list"),
    path("resources/<slug:slug>/", views.ResourceDetailView.as_view(), name="resource_detail"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("bundles/", views.BundleListView.as_view(), name="bundle_list"),
    path("bundles/<slug:slug>/", views.BundleDetailView.as_view(), name="bundle_detail"),

    # Загрузка ресурса
    path("upload/", views.resource_upload, name="resource_upload"),
]
