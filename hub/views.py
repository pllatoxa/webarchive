from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormView, DeleteView
from django.http import FileResponse, Http404

from .forms import (
    PostForm,
    CommentForm,
    ProjectForm,
    ProjectPostForm,
    ProjectCommentForm,
)
from .models import Post, Project, ProjectComment, ProjectPost, Comment


class ProjectListView(ListView):
    model = Project
    template_name = "hub/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Project.objects.select_related("owner")
            .prefetch_related("tags", "related_materials")
            .filter(visibility=Project.PUBLIC)
        )
        q = self.request.GET.get("q")
        owner = self.request.GET.get("owner")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(short_description__icontains=q))
        if owner:
            qs = qs.filter(owner__username__iexact=owner)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["owner"] = self.request.GET.get("owner", "")
        return ctx


class MyProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "hub/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        return (
            Project.objects.select_related("owner")
            .prefetch_related("tags", "related_materials")
            .filter(owner=self.request.user)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["my_projects"] = True
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = "hub/project_detail.html"
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        qs = Project.objects.select_related("owner").prefetch_related("tags", "related_materials")
        visibility_filter = Q(visibility=Project.PUBLIC) | Q(visibility=Project.UNLISTED)
        if self.request.user.is_authenticated:
            visibility_filter = visibility_filter | Q(owner=self.request.user)
        return qs.filter(visibility_filter)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["posts"] = self.object.posts.select_related("author").prefetch_related("comments")[:8]
        ctx["post_form"] = ProjectPostForm()
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = "hub/project_form.html"
    form_class = ProjectForm
    success_url = reverse_lazy("project_list")

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        if not form.cleaned_data.get("slug"):
            project.slug = slugify(project.title)[:170] or "project"
        project.generate_unique_slug()
        project.save()
        form.save_m2m()
        messages.success(self.request, "Проект создан и опубликован.")
        return redirect(self.success_url)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = "hub/project_confirm_delete.html"
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("project_list")

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "Удалять можно только свои проекты.")
        return redirect(self.get_object().get_absolute_url())


def project_download(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if not project.attachment:
        raise Http404("Файл не прикреплён")
    return FileResponse(
        project.attachment.open("rb"),
        as_attachment=True,
        filename=project.attachment.name.split("/")[-1],
    )


class ProjectPostListView(ListView):
    model = ProjectPost
    template_name = "hub/project_feed.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        qs = (
            ProjectPost.objects.select_related("project", "author")
            .prefetch_related("comments__author")
            .order_by("-created_at")
        )
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(project__title__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ProjectPostCreateView(LoginRequiredMixin, FormView):
    form_class = ProjectPostForm
    template_name = "hub/project_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.filter(slug=kwargs.get("slug")).first()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.project.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = self.project
        return ctx

    def form_valid(self, form):
        post = form.save(commit=False)
        post.project = self.project
        post.author = self.request.user
        post.save()
        messages.success(self.request, "Обсуждение создано.")
        return super().form_valid(form)


class ProjectPostDetailView(FormView):
    template_name = "hub/project_post_detail.html"
    form_class = ProjectCommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post = (
            ProjectPost.objects.select_related("project", "author")
            .prefetch_related("comments__author")
            .get(pk=kwargs["pk"])
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.post.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["post"] = self.post
        ctx["comments"] = self.post.comments.all()
        return ctx

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Нужно войти, чтобы комментировать.")
            return redirect("login")
        comment = form.save(commit=False)
        comment.post = self.post
        comment.author = self.request.user
        comment.save()
        messages.success(self.request, "Комментарий добавлен.")
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    template_name = "hub/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related("author").order_by("-created_at")


# Универсальные посты (без проекта) с комментариями
class PostDetailView(FormView):
    template_name = "hub/post_detail.html"
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404

        self.post = get_object_or_404(
            Post.objects.select_related("author").prefetch_related("comments__author"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["post"] = self.post
        ctx["comments"] = self.post.comments.all()
        return ctx

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Нужно войти, чтобы комментировать.")
            return redirect("login")
        comment = form.save(commit=False)
        comment.post = self.post
        comment.author = self.request.user
        comment.save()
        messages.success(self.request, "Комментарий добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.post.get_absolute_url()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "hub/post_form.html"
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, "Пост опубликован.")
        return redirect(self.success_url)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "hub/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")
    context_object_name = "post"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "Можно удалять только свои посты.")
        return redirect(post.get_absolute_url())
