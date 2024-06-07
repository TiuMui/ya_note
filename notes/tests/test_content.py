from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    LIST_PAGE = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.other_creator = User.objects.create(username='Другой Автор')
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            author=cls.creator,
        )

    def test_notes_list_for_creator(self):
        self.client.force_login(self.creator)
        response = self.client.get(self.LIST_PAGE)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_list_for_other_creator(self):
        self.client.force_login(self.other_creator)
        response = self.client.get(self.LIST_PAGE)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        slug = (self.note.slug,)
        url_names = (
            ('notes:add', None),
            ('notes:edit', slug),
        )
        for name, args in url_names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                self.client.force_login(self.creator)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.note = Note.objects.create(
            title='Проверка заголовка',
            text='Проверка текста',
            author=cls.creator,
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_content_detail_page(self):
        self.client.force_login(self.creator)
        response = self.client.get(self.detail_url)
        self.assertIn('note', response.context)
        note_object = response.context['note']
        note_title = note_object.title
        note_title_true = self.note.title
        self.assertEqual(note_title, note_title_true)
        note_text = note_object.text
        note_text_true = self.note.text
        self.assertEqual(note_text, note_text_true)
