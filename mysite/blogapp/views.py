from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView

from .models import Article


class ArticleDetailView(DetailView):
    model = Article
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
    )


class ArticlesListView(ListView):
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
    context_object_name = "articles"


# RSS
class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]
