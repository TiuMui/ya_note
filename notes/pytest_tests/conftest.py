import pytest

from django.test.client import Client

from notes.models import Note

@pytest.fixture
def creator(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def other_creator(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def creator_client(creator):
    client = Client()
    client.force_login(creator)
    return client


@pytest.fixture
def other_creator_client(other_creator):
    client = Client()
    client.force_login(other_creator)
    return client


@pytest.fixture
def note(creator):
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=creator,
    )
    return note


@pytest.fixture
def slug_for_args(note):  
    return (note.slug,)


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }

