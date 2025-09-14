from datetime import timedelta
from random import choice, randint, sample

from django.core.management.base import BaseCommand
from django.utils import timezone

from blogapp.models import Article, Author, Category, Tag


class Command(BaseCommand):
    help = 'Seeds the database with sample blog data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Authors
        authors_data = ['Alex Jons', 'Nick Smith', 'Cindy McDaniel']
        authors = []

        for name in authors_data:
            author, created = Author.objects.get_or_create(name=name, defaults={'bio': 'Author`s bio.'})
            authors.append(author)

        # Categories
        categories_data = ['Some category', 'Another category', 'Sample category']
        categories = []

        for name in categories_data:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)

        # Tags
        tags_data = ['Tag_1', 'Tag_2', 'Tag_3', 'Tag_4', 'Tag_5']
        tags = []

        for name in tags_data:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)

        # Articles
        article_titles = [
            "Введение в Django REST Framework",
            "10 простых рецептов итальянской пасты",
            "Гид по Праге: что посмотреть за выходные",
            "Будущее искусственного интеллекта",
            "Осенние тренды 2025: что носить?",
            "Как начать заниматься йогой дома",
            "Основы Docker для начинающих",
            "Секреты приготовления идеального стейка",
            "Путешествие по Норвежским фьордам",
            "Преимущества облачных вычислений",
        ]

        for article_id, title in enumerate(article_titles):
            author = choice(authors)
            category = choice(categories)

            current_time = timezone.now()
            time_delta = timedelta(days=randint(1, 365), hours=randint(1, 23), minutes=randint(1, 59))
            pub_date = current_time - time_delta

            content = (
                    f"Содержимое статьи '{title}'."
                    f"Здесь могло бы быть много интересного текста о {category.name}, написанного {author.name}."
                    "Это тестовый текст для заполнения базы данных." * randint(1,5)
            )

            article = Article.objects.create(
                title=title,
                content=content,
                pub_date=pub_date,
                author=author,
                category=category,
            )

            random_tags = sample(tags, k=min(randint(1, 3), len(tags)))
            article.tags.add(*random_tags)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
