from http import HTTPStatus

from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING


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

        cls.add_url = reverse('notes:add')
        cls.done_url = reverse('notes:success')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author_user,
            slug='note_slug')

        cls.form_note = {
            'title': 'Второй заголовок',
            'text': 'Текст формы',
            'slug': 'post_slug'
        }

        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse(
            'notes:delete', kwargs={'slug': cls.note.slug})

    def test_anonymous_user_cant_create_note(self):
        """
        Проверяем, что анонимный пользователь
        не может создать записку.
        """
        note_count = Note.objects.count()
        self.client.post(self.add_url, data=self.form_note)
        note_count_now = Note.objects.count()
        self.assertEqual(note_count_now, note_count)

    def test_user_can_create_note(self):
        """Проверяем, что авторизованный пользователь, может создать записку"""
        note_count = Note.objects.count()
        response = self.reader_client.post(self.add_url, data=self.form_note)
        note_count_now = Note.objects.count()
        self.assertEqual(note_count_now, note_count + 1)
        self.assertRedirects(response, self.done_url)
        note = Note.objects.latest('id')
        self.assertEqual(note.title, self.form_note['title'])
        self.assertEqual(note.text, self.form_note['text'])
        self.assertEqual(note.slug, self.form_note['slug'])
        self.assertEqual(note.author, self.reader_user)

    def test_user_cant_use_duplicate_slug(self):
        """Проверяем slug на уникальность."""
        note_count = Note.objects.count()
        self.form_note['slug'] = self.note.slug
        response = self.reader_client.post(self.add_url, data=self.form_note)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.form_note['slug'] + WARNING
        )
        note_count_now = Note.objects.count()
        self.assertEqual(note_count, note_count_now)

    def test_create_slug_for_slugify(self):
        """Проверяем создание slug при помощи slugify."""
        self.form_note.pop('slug')
        response = self.reader_client.post(self.add_url, data=self.form_note)
        result_slug = slugify(self.form_note['title'])
        self.assertRedirects(response, self.done_url)
        note = Note.objects.latest('id')
        self.assertEqual(note.slug, result_slug)

    def test_delete_note_author(self):
        """Проверяем, что пользователь может удалить свои заметки"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_edit_note_author(self):
        """Проверяем, что пользователь может редактировать свои заметки"""
        response = self.author_client.post(self.edit_url, data=self.form_note)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_note['text'])
        self.assertEqual(self.note.title, self.form_note['title'])
        self.assertEqual(self.note.slug, self.form_note['slug'])
        self.assertEqual(self.note.author, self.author_user)

    def test_delete_note_not_author(self):
        """Проверяем, что читатель не может удалить чужую запись."""
        response = self.author_client.post(self.edit_url, data=self.form_note)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_edit_note_not_author(self):
        """Проверяем, что читатель не может редактировать чужую запись."""
        response = self.reader_client.post(self.edit_url, data=self.form_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
