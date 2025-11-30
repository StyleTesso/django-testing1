from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(
        author_client,
        author,
        form_data,
        detail_url,
        news,
        redirect_detail_url
):
    """
    Проверяем,
    что авторизованный пользователь может оставить комментарий.
    """
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, redirect_detail_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url, redirect_login_url
):
    """
    Проверяем, что анонимный пользователь не может оставить комментарий
    и происходит redirect на страницу авторизации.
    """
    response = client.post(detail_url, data=form_data)
    assertRedirects(response, redirect_login_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(reader_client, detail_url):
    """
    Проверяем,
    что комментарий не создается, если в нем есть плохие слова.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = reader_client.post(detail_url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_note(
        author_client,
        edit_url,
        comment,
        form_data,
        redirect_detail_url
):
    """Проверяем, что автор комментария может его редактировать."""
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, redirect_detail_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(
        reader_client,
        form_data,
        comment,
        edit_url
):
    """Проверяем, что пользователь не может редактировать чужой комментарий."""
    response = reader_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
        author_client,
        delete_url,
        detail_url,
        redirect_detail_url
):
    """Проверяем, что автор комментария может его удалить."""
    response = author_client.post(delete_url)
    assertRedirects(response, redirect_detail_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(reader_client, delete_url):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
