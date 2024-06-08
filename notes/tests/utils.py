from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class MyTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.other_creator = User.objects.create(username='Другой Автор')
        cls.creator_client = Client()
        cls.creator_client.force_login(cls.creator)
        cls.other_creator_client = Client()
        cls.other_creator_client.force_login(cls.other_creator)
        cls.NOTE_TITLE = 'Заголовок заметки'
        cls.NOTE_TEXT = 'Текст заметки'
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.creator,
        )
        cls.url_home = reverse('notes:home')
        cls.url_signup = reverse('users:signup')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_add = reverse('notes:add')
        cls.url_list = reverse('notes:list')
        cls.url_success = reverse('notes:success')
        cls.url_edit_note_slug = reverse(
            'notes:edit', args=(cls.note.slug,)
        )
        cls.url_detail_note_slug = reverse(
            'notes:detail', args=(cls.note.slug,)
        )
        cls.url_delete_note_slug = reverse(
            'notes:delete', args=(cls.note.slug,)
        )
