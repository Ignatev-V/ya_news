"""Тестируем маршруты в pytest."""
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from .utils import (LOGIN_URL, LOGOUT_URL,
                    NEWS_DELETE_URL, NEWS_EDIT_URL, NEWS_HOME,
                    SIGNUP_URL)

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, client, expected_status',
    (
        (NEWS_HOME, Client(), HTTPStatus.OK),
        (LOGIN_URL, Client(), HTTPStatus.OK),
        (LOGOUT_URL, Client(), HTTPStatus.OK),
        (SIGNUP_URL, Client(), HTTPStatus.OK),
        (
            NEWS_DELETE_URL,
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            NEWS_DELETE_URL,
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            NEWS_EDIT_URL,
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            NEWS_EDIT_URL,
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
    ),
)
def test_pages_availability_for_different_users(
    url, client, expected_status, pk_for_args
):
    """Мегатест доступности страниц."""
    if url in (NEWS_EDIT_URL, NEWS_DELETE_URL):
        url = reverse(url, args=pk_for_args)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', (NEWS_DELETE_URL, NEWS_EDIT_URL))
def test_edit_delete_comment_redirect_for_anonymous(client, comment, name):
    """Проверка редиректов для анонима."""
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
