from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
EDIT_URL = pytest.lazy_fixture('edit_url')

REDIRECT_DELETE_URL = pytest.lazy_fixture('redirect_delete_url')
REDIRECT_EDIT_URL = pytest.lazy_fixture('redirect_edit_url')

CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, status',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, CLIENT, HTTPStatus.FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, CLIENT, HTTPStatus.FOUND),
    )
)
def test_pages(parametrized_client, url, status):
    """
    Проверяем, что главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы удаления и редактирования комментария доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    Страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны анонимным пользователям.
    """
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url, parametrized_client, status',
    (
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
    )
)
def test_logout(parametrized_client, url, status):
    """Проверяем, что logout доступен анонимному пользователю."""
    response = parametrized_client.post(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url, redirect',
    (
        (DELETE_URL, REDIRECT_DELETE_URL),
        (EDIT_URL, REDIRECT_EDIT_URL),
    )
)
def test_redirects(url, redirect, client):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    assertRedirects(client.get(url), redirect)
