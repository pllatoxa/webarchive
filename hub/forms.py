# hub/forms.py
from django import forms
from django.utils.text import slugify
from .models import Post, Comment, Project, ProjectPost, ProjectComment, Tag


class PostForm(forms.ModelForm):
    """Форма для создания постов с хештегами."""

    tags_raw = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input-control", "placeholder": "#python #django"}),
        label="Хештеги",
    )

    class Meta:
        model = Post
        fields = ["title", "body", "tags_raw"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input-control", "placeholder": "Заголовок"}),
            "body": forms.Textarea(attrs={"class": "input-control", "rows": 5, "placeholder": "Текст поста"}),
        }

    def clean_tags_raw(self):
        raw = self.cleaned_data.get("tags_raw", "") or ""
        parts = [p.strip().lstrip("#").lower() for p in raw.replace(",", " ").split()]
        tags = [p for p in parts if p]
        return list(dict.fromkeys(tags))  # уникальные, сохранённый порядок

    def parse_tags(self):
        """Создаёт/возвращает объекты Tag по введённым хештегам."""
        tags = []
        for name in self.cleaned_data.get("tags_raw", []):
            slug = slugify(name)[:60] or name
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tags.append(tag)
        return tags


class CommentForm(forms.ModelForm):
    """Форма для комментариев."""

    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ["body", "parent_id"]
        widgets = {
            "body": forms.Textarea(attrs={
                "class": "input-control",
                "rows": 3,
                "placeholder": "Ваш комментарий..."
            }),
        }


class ProjectForm(forms.ModelForm):
    """Создание/редактирование проекта (репозитория)."""

    class Meta:
        model = Project
        fields = ["title", "short_description", "readme", "github_url", "attachment", "visibility", "tags", "related_materials", "slug"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input-control"}),
            "short_description": forms.Textarea(attrs={"class": "input-control", "rows": 4}),
            "readme": forms.Textarea(attrs={"class": "input-control", "rows": 10}),
            "github_url": forms.URLInput(attrs={"class": "input-control"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "input-control", "accept": "*/*"}),
            "visibility": forms.HiddenInput(),
            "slug": forms.TextInput(attrs={"class": "input-control"}),
            "tags": forms.CheckboxSelectMultiple,
            "related_materials": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # slug опциональный
        self.fields["slug"].required = False
        # выставляем дефолтную видимость и делаем поле необязательным
        self.fields["visibility"].required = False
        self.fields["visibility"].initial = Project.PUBLIC


class ProjectPostForm(forms.ModelForm):
    """Пост внутри проекта."""

    class Meta:
        model = ProjectPost
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input-control"}),
            "body": forms.Textarea(attrs={"class": "input-control", "rows": 5}),
        }


class ProjectCommentForm(forms.ModelForm):
    """Комментарий к посту проекта."""

    class Meta:
        model = ProjectComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"class": "input-control", "rows": 3}),
        }
