from notes.forms import NoteForm
from .testing_utils import (
    FixtureCase,
    LIST_URL, ADD_URL, EDIT_URL
)


class TestContent(FixtureCase):
    def test_note_add_list(self):
        """
        Проверяем, что отдельная заметка передается на страницу
        со списком заметок.
        """
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        note = object_list.get(pk=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_note_not_in_list(self):
        """
        Проверяем, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.not_author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        """
        Проверяем, что на страницы создания
        и редактирования заметки передаются формы.
        """
        urls = (ADD_URL, EDIT_URL)
        for url in urls:
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertIsInstance(response.context.get('form'), NoteForm)
