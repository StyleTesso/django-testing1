from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

LIST_URL = reverse('notes:list')


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

    def test_new_note_in_list_notes(self):
        """
        Проверяем, что отдельная заметка передается на страницу
        со списком заметок.
        """
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_note_add_all_list(self):
        """
        Проверяем, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.reader_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_note_transmit_form(self):
        """Проверяем, что заметки передаются в формы."""
        slug = {'slug': self.note.slug}
        urls = (
            ('notes:edit', slug),
            ('notes:add', None)
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
