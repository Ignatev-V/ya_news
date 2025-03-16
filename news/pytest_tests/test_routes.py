"""Тестируем маршруты в pytest."""
from http import HTTPStatus

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client, expected_status',
    (
        ('news_home', Client(), HTTPStatus.OK),
        ('login_url', Client(), HTTPStatus.OK),
        ('logout_url', Client(), HTTPStatus.OK),
        ('signup_url', Client(), HTTPStatus.OK),
        (
            'news_delete_url',
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            'news_delete_url',
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            'news_edit_url',
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            'news_edit_url',
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
    ),
)
def test_pages_availability_for_different_users(
    url_fixture, client, expected_status, request
):
    """Мегатест доступности страниц."""
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news_delete_url', 'news_edit_url'))
def test_edit_delete_comment_redirect_for_anonymous(client, name,
                                                    request, login_url):
    """Проверка редиректов для анонима."""
    url = request.getfixturevalue(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
