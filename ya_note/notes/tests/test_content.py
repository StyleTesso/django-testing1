from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
            author=cls.author_user,
            slug='note_slug')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.add_url = reverse('notes:add')

    def test_note_note_add_all_list(self):
        """
        Проверяем, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        clients = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for client, expected_result in clients:
            with self.subTest(client=client, expected_result=expected_result):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected_result)

    def test_note_transmit_form(self):
        """Проверяем, что заметки передаются в формы."""
        urls = (self.edit_url, self.add_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
