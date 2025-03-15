"""Тесты логики для YaNews."""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS
from news.models import Comment
from .utils import LOGIN_URL, NEWS_DETAIL_URL, NEWS_DELETE_URL, NEWS_EDIT_URL

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_send_comment(client, news_page, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    cnt_comments_before = Comment.objects.count()
    response = client.post(url, data=form_data)
    expected_url = f'{LOGIN_URL}?next={url}'
    assertRedirects(response, expected_url)
    assert cnt_comments_before == Comment.objects.count() == 0


def test_auth_user_can_send_message(news_page, form_data,
                                    author_client, clear_database):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.news.pk == news_page.pk
    assert comment.author.pk == form_data.get('author')
    assert comment.text == form_data.get('text')


def test_comment_cant_contain_bad_words(author_client, news_page):
    """Проверка запрещенных слов в комменте."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = author_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors


def test_author_can_delete_his_comments(author_client, comment, news_page):
    """Авторизованный может редактировать или удалять свои комментарии."""
    url = reverse(NEWS_DELETE_URL, args=(comment.pk,))
    news_url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = author_client.delete(url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0


def test_author_can_edit_his_comments(
    author_client, comment, news_page, form_data
):
    """Авторизованный может редачить свои комменты."""
    url = reverse(NEWS_EDIT_URL, args=(comment.pk,))
    news_url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    form_data['text'] = 'New Text'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_url + '#comments')
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == form_data['text']
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_auth_user_cant_edit_other_comments(reader_client, comment, form_data):
    """Авторизованный не может редачить чужие комменты."""
    url = reverse(NEWS_EDIT_URL, args=(comment.pk,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_auth_user_cant_delete_other_comments(
    reader_client, comment, form_data
):
    """Авторизованный не может удалить чужой коммент."""
    url = reverse(NEWS_DELETE_URL, args=(comment.pk,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
