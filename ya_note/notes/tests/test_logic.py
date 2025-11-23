from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .testing_utils import (
    FixtureCase,

    ADD_URL,
    SUCCESS_URL,
    EDIT_URL,
    DELETE_URL
)


class TestLogic(FixtureCase):
    def test_anonymous_user_cant_create_note(self):
        """
        Проверяем, что анонимный пользователь не может
        создать заметку.
        """
        initial_count_notes = Note.objects.count()
        self.client.post(ADD_URL, data=self.form_data)
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, initial_count_notes)

    def test_user_can_create_note(self):
        """
        Проверяем, что залогиненный пользователь,
        может оставить заметку.
        """
        initial_count_notes = Note.objects.count()
        response = self.not_author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, f'{SUCCESS_URL}')
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, initial_count_notes + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.not_author_user)

    def test_user_cant_use_duplicate_slug(self):
        """
        Проверяем уникальность slug
        и перестраховываемся проверяя количество записей в БД.
        """
        initial_count_notes = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.not_author_client.post(ADD_URL, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.note.slug + WARNING
        )
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, initial_count_notes)

    def test_slug_generation_with_slugify(self):
        """
        Проверяем, что если не указан slug,
        он формируется с помощью slugify.
        """
        form_data_without_slug = {
            'title': 'Пример заголовка',
            'text': 'Пример текста заметки',
        }
        response = self.not_author_client.post(
            ADD_URL, data=form_data_without_slug)
        self.assertRedirects(response, f'{SUCCESS_URL}')
        note = Note.objects.latest('id')
        expected_slug = slugify(form_data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Проверяем, что автор заметки может удалить свою запись."""
        initial_count_notes = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, initial_count_notes - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверяем, что пользователь не может удалить чужую запись"""
        initial_count_notes = Note.objects.count()
        response = self.not_author_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, initial_count_notes)

    def test_author_can_edit_note(self):
        """Проверяем, что автор может редактировать свою заметку."""
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.title, self.form_data['title'])

    def test_user_cant_edit_comment_of_another_user(self):
        """Проверяем, что пользователь не может редактировать чужую запись"""
        response = self.not_author_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data['title'])
        self.assertNotEqual(self.note.text, self.form_data['text'])
        self.assertNotEqual(self.note.slug, self.form_data['slug'])
