"""Фикстуры для проекта."""
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


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
            title=f'Новость {index}',
            text=f'Текст новости {index}',
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
        text='Текст',
    )
    return comment


@pytest.fixture
def news_page():
    """Фикстура страницы новостей."""
    news_page = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news_page


@pytest.fixture
def comments(news_page, author):
    """Фикстура для создания комментариев."""
    now = timezone.now()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment(
            news=news_page,
            author=author,
            text=f'Текст комментария {index}',
        )
        comment.created = now - timedelta(minutes=index)
        comment.save()


@pytest.fixture
def login_url():
    """Фикстура для URL логина."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура для URL логаута."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура для URL авторизации."""
    return reverse('users:signup')


@pytest.fixture
def news_home():
    """Фикстура для URL Главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_delete_url(comment):
    """Фикстура для URL удаления комментария."""
    return reverse('news:delete', args=[comment.pk])


@pytest.fixture
def news_edit_url(comment):
    """Фикстура для URL редактирования комментария."""
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def news_detail_url(news_page):
    """Фикстура для URL редактирования комментария."""
    return reverse('news:detail', args=[news_page.pk])
