from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.creator)
        cls.post_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def test_cant_create_note_anonymous(self):
        self.client.post(self.url, data=self.post_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_can_create_note_user(self):
        response = self.auth_client.post(self.url, data=self.post_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        expected_slug = slugify(self.NOTE_TITLE)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, expected_slug)

    def test_cant_use_duble_slug(self):
        duble_slug = 'first_slug'
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.creator,
            slug=duble_slug
        )
        second_slug = {'slug': duble_slug}
        response = self.auth_client.post(self.url, data=second_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{duble_slug}{WARNING}'
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.other_creator = User.objects.create(username='Другой Автор')
        cls.creator_client = Client()
        cls.other_creator_client = Client()
        cls.creator_client.force_login(cls.creator)
        cls.other_creator_client.force_login(cls.other_creator)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.creator,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_success = reverse('notes:success')
        cls.post_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_creator_can_delete_note(self):
        response = self.creator_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_creator_can_edit_note(self):
        response = self.creator_client.post(self.edit_url, data=self.post_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_other_creator_cant_delete_note_creator(self):
        response = self.other_creator_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_other_creator_cant_edit_note_creator(self):
        response = self.other_creator_client.post(
            self.edit_url,
            data=self.post_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
