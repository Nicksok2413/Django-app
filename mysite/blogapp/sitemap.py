from django.contrib.sitemaps import Sitemap

from .models import Article


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def lastmod(self, obj: Article):
        return obj.published_at