from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


def save_profile(backend, user, response, *args, **kwargs):
    """
    После логина через Google:
    - обновляем user.email / first_name / last_name
    - создаём/обновляем Profile (nickname, avatar_url)
    """
    details = kwargs.get("details") or {}

    email = details.get("email")
    fullname = details.get("fullname") or details.get("username") or ""
    first_name = details.get("first_name")
    last_name = details.get("last_name")

    # ---- обновляем User ----
    if email and not user.email:
        user.email = email

    if not first_name and fullname:
        parts = fullname.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    user.save()

    # ---- профиль ----
    profile, _ = Profile.objects.get_or_create(user=user)

    # если ник пустой — ставим полное имя или username
    if not profile.nickname:
        profile.nickname = fullname or user.username

    picture_url = None
    if backend.name == "google-oauth2":
        picture_url = response.get("picture")  # Google обычно кладёт URL сюда

    if picture_url:
        profile.avatar_url = picture_url

    profile.save()