from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(author_client, form_data, detail_url):
    """
    Проверяем,
    что авторизованный пользователь может оставить комментарий.
    """
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url, login_url
):
    """
    Проверяем, что анонимный пользователь не может оставить комментарий
    и происходит redirect на страницу авторизации.
    """
    response = client.post(detail_url, data=form_data)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(reader_client, detail_url):
    """
    Проверяем,
    что комментарий не создается, если в нем есть плохие слова.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = reader_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_note(author_client,
                              edit_url,
                              comment,
                              form_data,
                              detail_url):
    """Проверяем, что автор комментария может его редактировать."""
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(reader_client,
                                      form_data,
                                      comment,
                                      edit_url):
    """Проверяем, что пользователь не может редактировать чужой комментарий."""
    response = reader_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    """Проверяем, что автор комментария может его удалить."""
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')


def test_other_user_cant_delete_comment(reader_client, delete_url):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
