"""Тесты логики для YaNews."""
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db

NEWS_FORM_DATA = {'text': "Текст"}


def clear_database(db):
    """Очистка базы данных."""
    db.objects.all().delete()


def test_anonymous_user_cant_send_comment(client, author, news_page,
                                          login_url, news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    data = NEWS_FORM_DATA.copy()
    cnt_comments_before = Comment.objects.count()
    response = client.post(news_detail_url, data=data)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert cnt_comments_before == Comment.objects.count()


def test_auth_user_can_send_comment(news_page, author_client,
                                    author, news_detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    clear_database(Comment)
    data = NEWS_FORM_DATA.copy()
    response = author_client.post(news_detail_url, data=data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.news.pk == news_page.pk
    assert comment.text == data['text']
    assert comment.author == author


def test_comment_cant_contain_bad_words(author_client, news_page,
                                        news_detail_url):
    """Проверка запрещенных слов в комменте."""
    cnt_comment_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    assert Comment.objects.count() == cnt_comment_before
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors


def test_author_can_delete_his_comments(author_client, comment, news_page,
                                        news_delete_url, news_detail_url):
    """Авторизованный может редактировать или удалять свои комментарии."""
    cnt_comment_before = Comment.objects.count()
    response = author_client.delete(news_delete_url)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == cnt_comment_before - 1


def test_author_can_edit_his_comments(
    author, author_client, comment, news_page, news_edit_url, news_detail_url
):
    """Авторизованный может редактировать свои комменты."""
    edit_data = {'text': 'Other Text'}
    response = author_client.post(news_edit_url, data=edit_data)
    assertRedirects(response, news_detail_url + '#comments')
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == edit_data['text']
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_auth_user_cant_edit_other_comments(reader, reader_client, news_page,
                                            comment, news_edit_url):
    """Авторизованный не может редачить чужие комменты."""
    edit_data = {'text': 'Other Text'}
    response = reader_client.post(news_edit_url, data=edit_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_auth_user_cant_delete_other_comments(reader_client, comment,
                                              news_delete_url):
    """Авторизованный не может удалить чужой коммент."""
    cnt_comment_before = Comment.objects.count()
    response = reader_client.delete(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == cnt_comment_before
