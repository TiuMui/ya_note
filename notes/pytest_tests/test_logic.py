from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


def test_user_can_create_note(creator_client, creator, form_data):
    url = reverse('notes:add')
    response = creator_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == creator


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0


def test_not_unique_slug(creator_client, note, form_data):
    url = reverse('notes:add')
    form_data['slug'] = note.slug
    response = creator_client.post(url, data=form_data)
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


def test_empty_slug(creator_client, form_data):
    url = reverse('notes:add')
    form_data.pop('slug')
    response = creator_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug


def test_author_can_edit_note(creator_client, form_data, note):
    url = reverse('notes:edit', args=(note.slug,))
    response = creator_client.post(url, form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_other_user_cant_edit_note(other_creator_client, form_data, note):
    true_title_note = note.title
    true_text_note = note.text
    true_slug_note = note.slug
    url = reverse('notes:edit', args=(note.slug,))
    response = other_creator_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note.refresh_from_db()
    note_from_db = Note.objects.get(id=note.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert true_title_note == note_from_db.title
    assert true_text_note == note_from_db.text
    assert true_slug_note == note_from_db.slug


def test_author_can_delete_note(creator_client, slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    response = creator_client.post(url)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 0


def test_other_user_cant_delete_note(other_creator_client, slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    response = other_creator_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
