from http import HTTPStatus

from .testing_utils import (
    FixtureCase,

    HOME_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    LIST_URL,
    ADD_URL,
    SUCCESS_URL,
    DETAIL_URL,
    EDIT_URL,
    DELETE_URL,
    REDIRECT_EDIT_URL,
    REDIRECT_ADD_URL,
    REDIRECT_DELETE_URL,
    REDIRECT_DETAIL_URL,
    REDIRECT_LIST_URL,
    REDIRECT_SUCCESS_URL
)


class TestRoutes(FixtureCase):
    def test_pages(self):
        """
        Проверяем, что Анонимному пользователю доступна главная страница.
        всем пользователям доступна страница входа и выхода с учетной записи.
        Страница отдельной записи, а также ее удаление и редактирование
        доступно только автору, если это не автор бросает ошибку 404.
        Если пользователь авторизован ему доступна страница со списком заметок,
        страница успешного добавления заметки и страница добавления заметки.
        """
        urls = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),

            (LIST_URL, self.not_author_client, HTTPStatus.OK),
            (ADD_URL, self.not_author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.not_author_client, HTTPStatus.OK),

            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),

            (DETAIL_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (EDIT_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.not_author_client, HTTPStatus.NOT_FOUND),

            (DETAIL_URL, self.client, HTTPStatus.FOUND),
            (EDIT_URL, self.client, HTTPStatus.FOUND),
            (DELETE_URL, self.client, HTTPStatus.FOUND),

            (ADD_URL, self.client, HTTPStatus.FOUND),
            (LIST_URL, self.client, HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, HTTPStatus.FOUND)
        )
        for url, client, status in urls:
            response = client.get(url)
            with self.subTest(url=url, status=status):
                self.assertEqual(response.status_code, status)

    def test_logout_post(self):
        """Тестируем logout методом post."""
        urls = (
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.author_client, HTTPStatus.OK),
            (LOGOUT_URL, self.not_author_client, HTTPStatus.OK)
        )
        for url, client, status in urls:
            response = client.post(url)
            with self.subTest(url=url, status=status):
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяем, что при попытке неавторизованного пользователя,
        зайти на страницу, редактирования комментария происходит
        redirect на страницу авторизации.
        """
        urls = (
            (ADD_URL, REDIRECT_ADD_URL),
            (DETAIL_URL, REDIRECT_DETAIL_URL),
            (DELETE_URL, REDIRECT_DELETE_URL),
            (EDIT_URL, REDIRECT_EDIT_URL),
            (LIST_URL, REDIRECT_LIST_URL),
            (SUCCESS_URL, REDIRECT_SUCCESS_URL)
        )
        for url, redirect_url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
