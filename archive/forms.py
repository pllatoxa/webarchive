from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Resource, Category, Profile
from hub.models import Post


User = get_user_model()


# =========================
#  АУТЕНТИФИКАЦИЯ
# =========================

class StyledRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Имя пользователя",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "Пароль",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "Повторите пароль",
            }
        )


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "Имя пользователя",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "Пароль",
            }
        )


class EmailRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "auth-input", "placeholder": "email@example.com"}),
    )


class EmailCodeForm(forms.Form):
    code = forms.CharField(
        label="Код из письма",
        max_length=6,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "6-значный код"}),
    )


# =========================
#  ФИЛЬТР РЕСУРСОВ (если понадобится)
# =========================

class ResourceFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input-control",
                "placeholder": "Что ищем?",
            }
        ),
    )

    category = forms.ModelChoiceField(
        label="Категория",
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "input-control"}),
    )

    resource_type = forms.ChoiceField(
        label="Тип",
        required=False,
        choices=[("", "Любой тип")] + list(Resource.TYPE_CHOICES),
        widget=forms.Select(attrs={"class": "input-control"}),
    )

    difficulty = forms.ChoiceField(
        label="Уровень",
        required=False,
        choices=[("", "Любой уровень")] + list(Resource.DIFFICULTY_CHOICES),
        widget=forms.Select(attrs={"class": "input-control"}),
    )

    language = forms.CharField(
        label="Язык",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input-control",
                "placeholder": "например, ru или en",
            }
        ),
    )

    ordering = forms.ChoiceField(
        label="Сортировать",
        required=False,
        choices=[
            ("-created_at", "Сначала новые"),
            ("created_at", "Сначала старые"),
            ("title", "По названию (А→Я)"),
            ("-title", "По названию (Я→А)"),
        ],
        widget=forms.Select(attrs={"class": "input-control"}),
    )


# =========================
#  ПРОФИЛЬ
# =========================

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nickname", "bio", "avatar"]

        widgets = {
            "nickname": forms.TextInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Ваш никнейм",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Коротко о себе",
                    "rows": 4,
                }
            ),
        }


# =========================
#  ЗАГРУЗКА ПРОЕКТА (Resource как проект)
# =========================

class ResourceUploadForm(forms.ModelForm):
    github_url = forms.URLField(
        label="GitHub URL (если есть)",
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "auth-input",
                "placeholder": "https://github.com/username/project",
            }
        ),
    )

    class Meta:
        model = Resource
        # 👇 только то, что показываем в форме
        fields = ["title", "full_description", "github_url"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Название проекта",
                    "style": "padding:0.9rem 1rem;",
                }
            ),
            "full_description": forms.Textarea(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Опишите проект, стек, идеи, ссылки...",
                    "rows": 10,
                    "style": "min-height:260px; padding:1rem 1.1rem;",
                }
            ),
        }


# =========================
#  ПОСТЫ (лента)
# =========================

class PostForm(forms.ModelForm):
    # НЕ модельное поле — сюда пишем хештеги
    tags_raw = forms.CharField(
        label="Хештеги",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "auth-input tag-input",
                "placeholder": "Введите хештеги через пробел или запятую (можно с #)...",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Post
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Заголовок поста",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "auth-input",
                    "placeholder": "Текст поста",
                    "rows": 6,
                }
            ),
        }
