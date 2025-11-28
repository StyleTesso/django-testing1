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
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.detail_url = reverse(
            'notes:detail', kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse(
            'notes:delete', kwargs={'slug': cls.note.slug})

    def test_home_and_authentication_page(self):
        """
        Проверяем, что Главная страница доступна анонимному пользователю.
        Страницы регистрации и  входа в учетную запись доступны всем
        пользователям.
        """
        urls = (
            (self.home_url, self.client),
            (self.login_url, self.client),
            (self.signup_url, self.client),
        )
        for url, users in urls:
            with self.subTest(url=url):
                response = users.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout(self):
        """
        Проверяем, что страница выхода с учетной записи доступна всем
        пользователям.
        """
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_notes(self):
        """
        Проверяем, что авторизованному пользователю доступны страницы
        со списком заметок, страница успешного добавления заметки и
        страница добавления заметки.
        """
        urls = (
            (self.list_url),
            (self.add_url),
            (self.success_url)
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_author(self):
        """
        Проверям, что страницы отдельной заметки, ее редактирование и
        удаление доступы только автору поста, а читателю возвращается
        ошибка 404.
        """
        clients = (
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        urls = (
            (self.detail_url),
            (self.edit_url),
            (self.delete_url),
        )
        for user, status in clients:
            for url in urls:
                with self.subTest(url=url, status=status, user=user):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """
        Проверяем перенаправление анонимного пользователя на
        страницу авторизации.
        """
        urls = (
            (self.add_url),
            (self.list_url),
            (self.success_url),
            (self.detail_url),
            (self.edit_url),
            (self.delete_url)
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
