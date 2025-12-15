# archive_site/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # 👈 добавили
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Основные страницы (home, лента, профиль, донаты и т.п.)
    path("", include("archive.urls")),
    # Проекты и связанные посты
    path("", include("hub.urls")),
    # Google OAuth (social_django)
    path("oauth/", include("social_django.urls", namespace="social")),

    # 🔥 ЛОГАУТ
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),  # после выхода — на главную
        name="logout",
    ),
] 

# Обслуживаем медиа-файлы прямо Django'ем, если разрешено флагом (например, на Render)
if settings.SERVE_MEDIA:
    from django.views.static import serve

    urlpatterns += [
        path(f"{settings.MEDIA_URL.lstrip('/') }<path:path>", serve, {"document_root": settings.MEDIA_ROOT})
    ]
