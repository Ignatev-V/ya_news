"""Тестируем контент."""


import pytest

from datetime import timedelta

from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.models import Comment
from .utils import NEWS_HOME, NEWS_DETAIL_URL


@pytest.mark.django_db
def test_news_per_page_on_home_page(client, news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse(NEWS_HOME)
    response = client.get(url)
    object_list = response.context['object_list']
    news_per_page = len(object_list)
    assert news_per_page == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sort_from_new_to_old(client, news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse(NEWS_HOME)
    response = client.get(url)
    object_list = response.context.get('object_list')
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_sort_from_old_to_new(news_page, author, client):
    """Проверка сортировки комментариев."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news_page,
            author=author,
            text=f"Текст комментария {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context.get('news')
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_user_hasnt_comment_form(client, news_page):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_auth_user_has_comment_form(news_page, admin_client):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = admin_client.get(url)
    assert 'form' in response.context
