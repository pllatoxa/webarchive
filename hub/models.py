# hub/models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Базовые справочники (дублируют archive-модели, но в пространстве hub)
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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="resources",
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(Tag, related_name="resources", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OTHER)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER)
    language = models.CharField(max_length=10, default="ru")
    download_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    affiliate_url = models.URLField(blank=True)
    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    uploaded_file = models.FileField(upload_to="uploads/", blank=True, null=True)
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


# =========================
# Проекты (как репозитории)
# =========================
class Project(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"

    VISIBILITY_CHOICES = [
        (PUBLIC, "Публичный"),
        (PRIVATE, "Приватный"),
        (UNLISTED, "По ссылке"),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    slug = models.SlugField(max_length=180, unique=True)
    title = models.CharField(max_length=200)
    short_description = models.TextField(blank=True)
    readme = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    attachment = models.FileField(upload_to="project_files/", blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default=PUBLIC)
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    related_materials = models.ManyToManyField(Resource, related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def generate_unique_slug(self):
        base = slugify(self.title)[:170] or "project"
        slug_candidate = base
        counter = 1
        while Project.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{base}-{counter}"
            counter += 1
        self.slug = slug_candidate
        return self.slug

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])


class ProjectPost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("project_post_detail", args=[self.pk])


class ProjectComment(models.Model):
    post = models.ForeignKey(ProjectPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.post}"


# =========================
# Общие посты (лента)
# =========================
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("post_list")

    @property
    def author_display_name(self):
        """
        Имя автора для отображения: ник из профиля, иначе username.
        """
        try:
            profile = self.author.profile
            if profile.nickname:
                return profile.nickname
        except Exception:
            pass
        return self.author.username

    @property
    def dislike_count(self):
        # Считаем количество дизлайков по реакциям
        return self.reactions.filter(value=PostLike.DISLIKE).count()

    @property
    def comment_count(self):
        return self.comments.count()


class PostLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = (
        (LIKE, "like"),
        (DISLIKE, "dislike"),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reactions")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} {self.get_value_display()} {self.post_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hub_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.post}"
