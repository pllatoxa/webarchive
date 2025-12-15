from django.views.generic import ListView
from .models import DonationLink
from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import get_user_model, login

from hub.models import Post
from hub.forms import CommentForm

User = get_user_model()
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Все комментарии к посту
    comments = (
        post.comments.select_related("author", "author__profile")
        .prefetch_related("replies__author", "replies__author__profile")
        .order_by("created_at")
    )

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = form.cleaned_data.get("parent_id")
            if parent_id:
                parent = post.comments.filter(pk=parent_id).first()
                if parent:
                    comment.parent = parent
            comment.save()
            # после отправки коммента перезагружаем страницу поста
            return redirect("post_detail", pk=post.pk)
    else:
        form = CommentForm()

    return render(
        request,
        "hub/post_detail.html",   # <-- если шаблон у тебя по-другому называется/лежит, поменяй путь
        {
            "post": post,
            "comments": comments,
            "form": form,
        },
    )

@login_required
def profile_view(request):
    return render(request, "archive/profile.html", {
        "user": request.user,
    })

from django.utils.text import slugify
from django.views.generic import (

    DetailView,
    FormView,
    ListView,
    TemplateView,
)

from django.contrib.auth.decorators import login_required

# МОДЕЛИ
from hub.models import Post
from .models import (
    Bundle,
    Category,
    DonationLink,
    Resource,
    Profile,
    Tag,
)

# ФОРМЫ
from .forms import (
    ProfileForm,
    ResourceFilterForm,
    ResourceUploadForm,
    StyledRegistrationForm,
    PostForm,
)

from django.shortcuts import render
# остальные импорты оставь как есть


from django.shortcuts import redirect

from django.shortcuts import render

def home(request):
    return render(request, "archive/home.html", {})

# -------------------------------
# ГЛАВНАЯ СТРАНИЦА
# -------------------------------
class HomePageView(TemplateView):
    template_name = "archive/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.annotate(
            resource_count=Count("resources")
        ).order_by("name")

        context["featured_resources"] = (
            Resource.objects.filter(is_published=True, is_featured=True)
            .select_related("category")
            .prefetch_related("tags")[:6]
        )

        context["latest_resources"] = (
            Resource.objects.filter(is_published=True)
            .select_related("category")
            .prefetch_related("tags")[:8]
        )

        context["donation_links"] = DonationLink.objects.filter(is_active=True)
        context["ai_tools"] = Resource.objects.filter(
            type=Resource.AI_TOOLS,
            is_published=True,
        )[:6]

        return context


# -------------------------------
# РЕСУРСЫ
# -------------------------------
class ResourceListView(ListView):
    model = Resource
    template_name = "archive/resource_list.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Resource.objects.filter(is_published=True)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        self.filter_form = ResourceFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data

            if data.get("q"):
                q = data["q"]
                queryset = queryset.filter(
                    Q(title__icontains=q)
                    | Q(description__icontains=q)
                    | Q(full_description__icontains=q)
                )

            if data.get("category"):
                queryset = queryset.filter(category=data["category"])

            if data.get("resource_type"):
                queryset = queryset.filter(type=data["resource_type"])

            if data.get("difficulty"):
                queryset = queryset.filter(difficulty=data["difficulty"])

            if data.get("language"):
                queryset = queryset.filter(language__iexact=data["language"])

            if data.get("ordering"):
                queryset = queryset.order_by(data["ordering"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", ResourceFilterForm())

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()

        return context


class ResourceDetailView(DetailView):
    model = Resource
    template_name = "archive/resource_detail.html"
    context_object_name = "resource"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Resource.objects.filter(is_published=True)
            .select_related("category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.object

        tag_ids = list(resource.tags.values_list("id", flat=True))
        queryset = Resource.objects.filter(is_published=True).exclude(id=resource.id)

        if resource.category:
            queryset = queryset.filter(
                Q(category=resource.category) | Q(tags__in=tag_ids)
            ).distinct()
        else:
            queryset = queryset.filter(tags__in=tag_ids).distinct()

        context["related_resources"] = queryset[:4]
        return context


# -------------------------------
# КАТЕГОРИИ
# -------------------------------
class CategoryListView(ListView):
    model = Category
    template_name = "archive/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(
            resource_count=Count("resources")
        ).order_by("name")


class CategoryDetailView(ListView):
    model = Resource
    template_name = "archive/category_detail.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs["slug"])

    def get_queryset(self):
        category = self.get_category()

        queryset = (
            Resource.objects.filter(category=category, is_published=True)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        self.filter_form = ResourceFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data

            if data.get("q"):
                q = data["q"]
                queryset = queryset.filter(
                    Q(title__icontains=q)
                    | Q(description__icontains=q)
                    | Q(full_description__icontains=q)
                )

            if data.get("resource_type"):
                queryset = queryset.filter(type=data["resource_type"])

            if data.get("difficulty"):
                queryset = queryset.filter(difficulty=data["difficulty"])

            if data.get("language"):
                queryset = queryset.filter(language__iexact=data["language"])

            if data.get("ordering"):
                queryset = queryset.order_by(data["ordering"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()

        context["filter_form"] = getattr(self, "filter_form", ResourceFilterForm())

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()

        return context


# -------------------------------
# BUNDLES
# -------------------------------
class BundleListView(ListView):
    model = Bundle
    template_name = "archive/bundle_list.html"
    context_object_name = "bundles"

    def get_queryset(self):
        return (
            Bundle.objects.filter(is_active=True)
            .prefetch_related("resources")
            .order_by("title")
        )


class BundleDetailView(DetailView):
    model = Bundle
    template_name = "archive/bundle_detail.html"
    context_object_name = "bundle"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Bundle.objects.filter(is_active=True)
            .prefetch_related("resources__category", "resources__tags")
        )


# -------------------------------
# ДОНАТ
# -------------------------------
class DonationPageView(TemplateView):
    template_name = "archive/donate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["donation_links"] = DonationLink.objects.filter(is_active=True)
        return context


# -------------------------------
# AI Tools
# -------------------------------
class AIToolsListView(ListView):
    model = Resource
    template_name = "archive/ai_tools.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_queryset(self):
        return (
            Resource.objects.filter(type=Resource.AI_TOOLS, is_published=True)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-created_at")
        )


# -------------------------------
# ЗАГРУЗКА РЕСУРСА
# -------------------------------
class ResourceUploadView(LoginRequiredMixin, FormView):
    template_name = "archive/upload.html"
    form_class = ResourceUploadForm
    success_url = reverse_lazy("resource_list")
    login_url = reverse_lazy("login")

    def generate_slug(self, title):
        base = slugify(title)[:200] or "resource"
        slug = base
        counter = 1

        while Resource.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    def form_valid(self, form):
        resource = form.save(commit=False)
        resource.slug = self.generate_slug(resource.title)
        resource.is_published = True
        resource.source_name = self.request.user.username

        resource.save()
        form.save_m2m()

        messages.success(self.request, "Материал опубликован.")
        return super().form_valid(form)


# -------------------------------
# РЕГИСТРАЦИЯ
# -------------------------------
class RegisterView(FormView):
    template_name = "archive/register.html"
    form_class = StyledRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация успешна!")
        return super().form_valid(form)


# -------------------------------
# ПРОФИЛЬ
# -------------------------------
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "archive/profile.html", {
        "form": form,
        "profile": profile,
    })


from django.views.generic import FormView, ListView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from hub.models import Post
from archive.models import Tag
from archive.forms import PostForm


# -------------------------------
# ЛЕНТА ПОСТОВ
# -------------------------------
from django.views.generic import ListView
from django.db.models import Q

from hub.models import Post


class ProjectFeedView(ListView):
    """
    Лента постов (как реддит / инста, просто список Post)
    """
    model = Post
    template_name = "archive/project_feed.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Post.objects
            .select_related("author", "author__profile")
            .prefetch_related("reactions")
            .order_by("-created_at")
        )

        q = self.request.GET.get("q")
        if q:
            # Базовый поиск в БД
            qs_db = qs.filter(
                Q(title__icontains=q) |
                Q(body__icontains=q) |
                Q(author__username__icontains=q)
                # | Q(tags__name__icontains=q)  # <-- ТОЖЕ УБРАЛИ
            ).distinct()

            # Дополнительно — Python casefold для кириллицы (SQLite не всегда делает icontains без учёта регистра)
            q_cf = q.casefold()
            ids_py = []
            for p in qs:
                title = (p.title or "").casefold()
                body = (p.body or "").casefold()
                nick = (getattr(p.author.profile, "nickname", "") or "").casefold()
                username = (p.author.username or "").casefold()
                if (
                    q_cf in title
                    or q_cf in body
                    or q_cf in nick
                    or q_cf in username
                ):
                    ids_py.append(p.id)

            ids_all = list(qs_db.values_list("id", flat=True)) + ids_py
            qs = qs.filter(id__in=ids_all).distinct()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx

# archive/views.py — в самом низу

from django.shortcuts import redirect
from django.views.generic import DetailView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import F
from django.shortcuts import get_object_or_404

from hub.models import Post, PostLike
from hub.forms import PostForm, CommentForm


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "archive/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = form.save(commit=False)
        post.save()
        tags = form.parse_tags()
        if tags:
            post.tags.set(tags)
        return redirect("project_feed")


class PostDetailView(DetailView):
    model = Post
    template_name = "archive/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comments"] = self.object.comments.all()
        ctx["form"] = CommentForm()
        return ctx

    def post(self, request, *args, **kwargs):
        # обработка формы комментария
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")  # или куда тебе нужно

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect("project_feed")

        ctx = self.get_context_data()
        ctx["form"] = form
        return self.render_to_response(ctx)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "archive/post_confirm_delete.html"
    success_url = reverse_lazy("project_feed")

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


# Лайки / дизлайки
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


def _recalc_likes(post):
    likes = PostLike.objects.filter(post=post, value=PostLike.LIKE).count()
    Post.objects.filter(pk=post.pk).update(likes_count=likes)


@login_required
@require_POST
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    reaction, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={"value": PostLike.LIKE},
    )
    if not created and reaction.value != PostLike.LIKE:
        reaction.value = PostLike.LIKE
        reaction.save(update_fields=["value"])
    _recalc_likes(post)
    return redirect("project_feed")


@login_required
@require_POST
def post_dislike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    reaction, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={"value": PostLike.DISLIKE},
    )
    if not created and reaction.value != PostLike.DISLIKE:
        reaction.value = PostLike.DISLIKE
        reaction.save(update_fields=["value"])
    _recalc_likes(post)
    return redirect("project_feed")
    
# archive/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ResourceUploadForm  # у тебя такая форма уже есть, раз он её подсказал

@login_required
def resource_upload(request):
    if request.method == "POST":
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save()
            # если у модели Resource есть get_absolute_url — отправляем туда
            return redirect(resource.get_absolute_url())
    else:
        form = ResourceUploadForm()

    return render(request, "archive/resource_upload.html", {"form": form})

class DonateView(ListView):
    model = DonationLink
    template_name = "archive/donate.html"   # или путь к твоему шаблону донатов
    context_object_name = "links"          # как будем обращаться к списку в шаблоне

    def get_queryset(self):
        # показываем только активные ссылки
        return DonationLink.objects.filter(is_active=True).order_by("title")
