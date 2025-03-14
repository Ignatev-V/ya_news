"""Тестируем маршруты в pytest."""
import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

NEWS_HOME = 'news:home'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'
NEWS_DELETE_URL = 'news:delete'
NEWS_EDIT_URL = 'news:edit'
NEWS_DETAIL_URL = 'news:detail'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (NEWS_HOME, LOGIN_URL, LOGOUT_URL, SIGNUP_URL)
)
def test_pages_avaliability_for_anonymous_user(client, name):
    """Тестируем достусность страниц для анонима."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_page_avaliability_for_anonymous_user(client, news_page):
    """Страница отдельной новости доступна анониму."""
    url = reverse(NEWS_DETAIL_URL, args=(news_page.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', (NEWS_DELETE_URL, NEWS_EDIT_URL))
def test_edit_delete_comment_redirect_for_anonymous(client, comment, name):
    """Редактирование и удаление недоступно Анониму."""
    login_url = reverse(LOGIN_URL)
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize('name', (NEWS_DELETE_URL, NEWS_EDIT_URL))
def test_edit_delete_pages_avaliability_for_different_users(
    parametrized_client, expected_status, name, comment
):
    """Доступность редактирования и удаления для разных пользователей."""
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
