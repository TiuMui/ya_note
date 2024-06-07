from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create(username='Автор Заметки')
        cls.other_creator = User.objects.create(username='Другой Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.creator,
        )

    def test_pages_availability_anonymous(self):
        url_names = (
            'notes:home',
            'users:signup',
            'users:login',
            'users:logout',
        )
        for name in url_names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_authorized(self):
        url_names = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        self.client.force_login(self.other_creator)
        for name in url_names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_creator(self):
        user_statuses = (
            (self.creator, HTTPStatus.OK),
            (self.other_creator, HTTPStatus.NOT_FOUND),
        )
        url_names = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in url_names:
                with self.subTest(name=name, status=status):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        slug = (self.note.slug,)
        url_names = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:edit', slug),
            ('notes:detail', slug),
            ('notes:delete', slug),
            ('notes:list', None)
        )
        login_url = reverse('users:login')
        for name, args in url_names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
