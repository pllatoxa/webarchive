from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("category_detail", args=[self.slug])


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Resource(models.Model):
    MANUAL = "manual"
    SCRIPT = "script"
    FILE = "file"
    BOOK = "book"
    PODCAST = "podcast"
    FOOTAGE = "footage"
    AI_TOOLS = "ai_tools"
    OTHER = "other"

    TYPE_CHOICES = [
        (MANUAL, "Мануал / Гайд"),
        (SCRIPT, "Скрипт / Сниппет"),
        (FILE, "Файл / Шпаргалка"),
        (BOOK, "Книга"),
        (PODCAST, "Подкаст"),
        (FOOTAGE, "Футаж / Медиа"),
        (AI_TOOLS, "AI-инструменты"),
        (OTHER, "Другое"),
    ]

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

    DIFFICULTY_CHOICES = [
        (BEGINNER, "Новичок"),
        (INTERMEDIATE, "Средний"),
        (ADVANCED, "Продвинутый"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)

    description = models.CharField(max_length=400, blank=True)
    full_description = models.TextField(blank=True)

    # 👇 Делаем категорию НЕобязательной (чтобы форма проекта была простой)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="resources",
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(Tag, related_name="resources", blank=True)

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OTHER)
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER
    )
    language = models.CharField(max_length=10, default="ru")

    download_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    affiliate_url = models.URLField(blank=True)

    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)

    uploaded_file = models.FileField(upload_to="uploads/", blank=True, null=True)

    # 👇 Новое поле для GitHub (можно использовать именно под проекты)
    github_url = models.URLField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("resource_detail", args=[self.slug])


class DonationLink(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Донат-ссылка"
        verbose_name_plural = "Донат-ссылки"
    ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Bundle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    resources = models.ManyToManyField(Resource, related_name="bundles", blank=True)
    is_active = models.BooleanField(default=True)
    purchase_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Подборка / Bundle"
        verbose_name_plural = "Подборки / Bundles"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("bundle_detail", args=[self.slug])


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    nickname = models.CharField("Никнейм", max_length=40, blank=True)
    bio = models.TextField("Описание", max_length=500, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    avatar_url = models.URLField("Аватар (Google URL)", blank=True, null=True)

    def __str__(self):
        return self.nickname or self.user.username
    
# hub/models.py
from django.conf import settings
from django.db import models


class Post(models.Model):
    # ... у тебя уже есть
    pass


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="archive_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class EmailLoginCode(models.Model):
    """
    Одноразовый код для входа по email.
    """
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.code})"
