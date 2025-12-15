from django.contrib import admin

from .models import Bundle, Category, DonationLink, Resource, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'type',
        'difficulty',
        'language',
        'is_published',
        'is_featured',
        'created_at',
    )
    list_filter = (
        'category',
        'type',
        'difficulty',
        'language',
        'is_published',
        'is_featured',
        'tags',
    )
    search_fields = ('title', 'description', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('tags',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DonationLink)
class DonationLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('resources',)
