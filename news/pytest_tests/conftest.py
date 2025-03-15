"""Фикстуры для проекта."""
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def author(django_user_model):
    """Фикстура создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Фикстура создания читателя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Вызываем фикстуру автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура создания клиента Читателя."""
    reader_client = Client()
    reader_client.force_login(reader)
    return reader_client


@pytest.fixture
def news():
    """Фикстура создания новостей."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f"Новость {index}",
            text=f"Текст новости {index}",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news_page):
    """Фикстура создания заметки Автором."""
    comment = Comment.objects.create(
        news=news_page,
        author=author,
        text="Текст",
    )
    return comment


@pytest.fixture
def news_page():
    """Фикстура страницы новостей."""
    news_page = News.objects.create(
        title="Заголовок новости",
        text="Текст новости",
    )
    return news_page


@pytest.fixture
def comments(news_page, author):
    """Фикстура для создания комментариев."""
    now = timezone.now()
    comments_list = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news_page,
            author=author,
            text=f"Текст комментария {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


@pytest.fixture
def form_data(news_page, author):
    """Фикстура полей формы."""
    return {
        'news': news_page.pk,
        'author': author.pk,
        'text': "Текст",
    }


@pytest.fixture
def pk_for_args(comment):
    """Фикстура ид коммента."""
    return (comment.pk,)


@pytest.fixture(autouse=True)
def clear_database(db):
    """Фикстура для очистки базы данных перед каждым тестом."""
    yield  # Тест будет выполнен здесь
    Comment.objects.all().delete()
