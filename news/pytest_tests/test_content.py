"""Тестируем контент."""
import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm
from .utils import NEWS_HOME, NEWS_DETAIL_URL


pytestmark = pytest.mark.django_db


def test_news_per_page_on_home_page(client, news):
    """Проверка на количество новостей на главной странице."""
    response = client.get(NEWS_HOME)
    news_per_page = response.context['object_list'].count()
    assert news_per_page == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sort_from_new_to_old(client, news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(NEWS_HOME)
    object_list = response.context.get('object_list')
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_sort_from_old_to_new(news_page, client, comments):
    """Проверка сортировки комментариев."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context.get('news')
    all_comments = list(news.comment_set.all())
    all_comments_sorted = sorted(all_comments, key=lambda c: c.created)
    assert all_comments == all_comments_sorted


def test_anonymous_user_hasnt_comment_form(client, news_page):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = client.get(url)
    assert 'form' not in response.context


def test_auth_user_has_comment_form(news_page, admin_client):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = admin_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
