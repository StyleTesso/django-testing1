from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader_user = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader_user)

        cls.author_user = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author_user)

    def test_home_and_authentication_page(self):
        """
        Проверяем, что Главная страница доступна анонимному пользователю.
        Страницы регистрации и  входа в учетную запись доступны всем
        пользователям.
        """
        urls = (
            ('notes:home', self.client),
            ('users:login', self.author_client),
            ('users:login', self.reader_client),
            ('users:login', self.client),
            ('users:signup', self.client),
            ('users:signup', self.reader_client),
            ('users:signup', self.author_client),
        )
        for name, users in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = users.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout(self):
        """
        Проверяем, что страница выхода с учетной записи доступна всем
        пользователям.
        """
        urls = (
            ('users:logout', self.client),
            ('users:logout', self.author_client),
            ('users:logout', self.reader_client)
        )
        for name, users in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = users.post(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_notes(self):
        """
        Проверяем, что авторизованному пользователю доступны страницы
        со списком заметок, страница успешного добавления заметки и
        страница добавления заметки.
        """
        urls = (
            ('notes:list'),
            ('notes:add'),
            ('notes:success')
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_author(self):
        """
        Проверям, что страницы отдельной заметки, ее редактирование и
        удаление доступы только автору поста, а читателю возвращается
        ошибка 404.
        """
        slug = {'slug': self.note.slug}
        urls = (
            ('notes:detail', slug,
             self.author_client, HTTPStatus.OK),
            ('notes:edit', slug,
             self.author_client, HTTPStatus.OK),
            ('notes:delete', slug,
             self.author_client, HTTPStatus.OK),
            ('notes:detail', slug,
             self.reader_client, HTTPStatus.NOT_FOUND),
            ('notes:edit', slug,
             self.reader_client, HTTPStatus.NOT_FOUND),
            ('notes:delete', slug,
             self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, kwargs, client, status in urls:
            with self.subTest(name=name, status=status):
                url = reverse(name, kwargs=kwargs)
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """
        Проверяем перенаправление анонимного пользователя на
        страницу авторизации.
        """
        slug = {'slug': self.note.slug}
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug)
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
