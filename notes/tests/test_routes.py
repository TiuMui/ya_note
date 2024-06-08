from http import HTTPStatus

from notes.tests.utils import MyTestCase


class TestRoutes(MyTestCase):

    def test_pages_availability_anonymous(self):
        url_names = (
            self.url_home,
            self.url_signup,
            self.url_login,
            self.url_logout,
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = url_name
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_authorized(self):
        url_names = (
            self.url_add,
            self.url_list,
            self.url_success,
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = url_name
                response = self.other_creator_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_creator(self):
        user_statuses = (
            (self.creator_client, HTTPStatus.OK),
            (self.other_creator_client, HTTPStatus.NOT_FOUND),
        )
        url_names = (
            self.url_edit_note_slug,
            self.url_detail_note_slug,
            self.url_delete_note_slug,
        )
        for logged_client, status in user_statuses:
            for url_name in url_names:
                with self.subTest(
                    url_name=url_name,
                    logged_client=logged_client,
                    status=status
                ):
                    url = url_name
                    response = logged_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        url_names = (
            self.url_add,
            self.url_success,
            self.url_edit_note_slug,
            self.url_detail_note_slug,
            self.url_delete_note_slug,
            self.url_list
        )
        login_url = self.url_login
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = url_name
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
