from django.contrib import admin

from .models import Article


class TagInline(admin.StackedInline):
    model = Article.tags.through


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
    ]
    list_display = "id", "title", "body", "published_at", "author", "category"

    def get_queryset(self, request):
        return Article.objects.select_related("author", "category").prefetch_related("tags")
