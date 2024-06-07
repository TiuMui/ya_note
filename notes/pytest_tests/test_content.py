from django.urls import reverse
from notes.forms import NoteForm
import pytest


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (pytest.lazy_fixture('creator_client'), True),
        (pytest.lazy_fixture('other_creator_client'), False),
    )
)
def test_notes_list_for_different_users(
        note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(creator_client, name, args):
    url = reverse(name, args=args)
    response = creator_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
