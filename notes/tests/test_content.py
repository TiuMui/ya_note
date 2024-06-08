from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.utils import MyTestCase

User = get_user_model()


class TestListPage(MyTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_notes_list_for_creator(self):
        response = self.creator_client.get(self.url_list)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_for_other_creator(self):
        response = self.other_creator_client.get(self.url_list)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_pages_contains_form(self):
        url_names = (
            self.url_add,
            self.url_edit_note_slug,
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = url_name
                self.client.force_login(self.creator)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)


class TestDetailPage(MyTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_content_detail_page(self):
        response = self.creator_client.get(self.url_detail_note_slug)
        self.assertIn('note', response.context)
        note_object = response.context['note']
        note_title = note_object.title
        note_title_true = self.note.title
        self.assertEqual(note_title, note_title_true)
        note_text = note_object.text
        note_text_true = self.note.text
        self.assertEqual(note_text, note_text_true)
