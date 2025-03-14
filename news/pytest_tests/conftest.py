"""Фикстуры для проекта."""
# conftest.py
import pytest

from datetime import datetime, timedelta

from django.conf import settings

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    """Фикстура создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура не для автора."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Вызываем фикстуру автора."""
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура создания клиента НеАвтора."""
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


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
        text="Текст коммента",
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
def slug_for_args(note):
    """Фикстура запрашивает другую фикстуру создания заметки."""
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (news.slug,)
