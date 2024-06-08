from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import MyTestCase

User = get_user_model()


class TestNoteCreation(MyTestCase):
    OTHER_NOTE_TITLE = 'Какой-то заголовок'
    OTHER_NOTE_TEXT = 'Какой-то текст'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.post_data = {
            'title': cls.OTHER_NOTE_TITLE,
            'text': cls.OTHER_NOTE_TEXT
        }

    def test_cant_create_note_anonymous(self):
        before_count = Note.objects.count()
        self.client.post(self.url_add, data=self.post_data)
        after_count = Note.objects.count()
        self.assertEqual(before_count, after_count)

    def test_can_create_note_user(self):
        Note.objects.all().delete()
        before_count = Note.objects.count()
        response = self.creator_client.post(self.url_add, data=self.post_data)
        self.assertRedirects(response, self.url_success)
        after_count = Note.objects.count()
        self.assertEqual(before_count + 1, after_count)
        expected_slug = slugify(self.OTHER_NOTE_TITLE)
        note = Note.objects.get()
        self.assertEqual(note.title, self.OTHER_NOTE_TITLE)
        self.assertEqual(note.text, self.OTHER_NOTE_TEXT)
        self.assertEqual(note.slug, expected_slug)

    def test_cant_use_duble_slug(self):
        duble_slug = slugify(self.NOTE_TITLE)
        second_slug = {'slug': duble_slug}
        before_count = Note.objects.count()
        response = self.creator_client.post(self.url_add, data=second_slug)
        after_count = Note.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{duble_slug}{WARNING}'
        )


class TestNoteEditDelete(MyTestCase):
    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.post_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_creator_can_delete_note(self):
        before_count = Note.objects.count()
        response = self.creator_client.delete(self.url_delete_note_slug)
        self.assertRedirects(response, self.url_success)
        after_count = Note.objects.count()
        self.assertEqual(before_count - 1, after_count)

    def test_creator_can_edit_note(self):
        response = self.creator_client.post(self.url_edit_note_slug, data=self.post_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.author, self.creator)

    def test_other_creator_cant_delete_note_creator(self):
        before_count = Note.objects.count()
        response = self.other_creator_client.delete(self.url_delete_note_slug)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_count = Note.objects.count()
        self.assertEqual(before_count, after_count)

    def test_other_creator_cant_edit_note_creator(self):
        response = self.other_creator_client.post(
            self.url_edit_note_slug,
            data=self.post_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.creator)
