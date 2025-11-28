from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('home_url')),
        (pytest.lazy_fixture('login_url')),
        (pytest.lazy_fixture('signup_url')),
        (pytest.lazy_fixture('detail_url'))
    )
)
def test_pages_availability_for_anonymous_user(client, url):
    """
    Проверяем, доступность главной сраницы, страницы авторизации,
    сраницы отдельного поста и страницы регистрации для анонимного
    пользователя.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout(client):
    """Проверяем, что анонимному пользователю доступна страница logout"""
    response = client.post(reverse('users:logout'))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('delete_url'))
    )
)
def test_edit_and_delete_comment(
    url,
    parametrized_client,
    expected_status
):
    """
    Проверяем, что страницы редактирования и удаления комментария
    доступны автору, а обычному пользователю возвращается ошибка 404.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('delete_url'))
    )
)
def test_redirects_anonyomus(url, client):
    """
    Проверяем, что анонмный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
