from http import HTTPStatus

import pytest
from django.test.client import Client
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db
client = Client()
# Делаем форму для post запроса.
FORM_DATA = {'text': 'Новый текст'}
# Делаем форму для post запроса.
BAD_FORM_DATA = [
    {'text': f'** ***, *** hhhhh {bad_word} hhhhh. hhh'}
    for bad_word in BAD_WORDS
]


def test_user_can_create_comment(
        not_author_client, detail_url,
        news,
        redirect_detail_comments):
    """
    Проверяем, что авторизованный пользователь
    может оставить комментарий.
    """
    response = not_author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, redirect_detail_comments)
    assert response.status_code == HTTPStatus.FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']


def test_anonymous_cant_create_comment(client, detail_url):
    """
    Проверяем, что анонимный пользователь
    не может комментировать новость.
    """
    response = client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'data_with_bad_word', BAD_FORM_DATA
)
def test_user_cant_use_bad_words(
        not_author_client,
        detail_url,
        data_with_bad_word
):
    """Проверяем, что комментарий не создается если в нем есть плохие слова."""
    response = not_author_client.post(detail_url, data=data_with_bad_word)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_delete_comment(author_client, news, comment, delete_url):
    """Проверяем, что автор может удалить свой комментарий."""
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_not_author_cant_delete_comment(
        not_author_client,
        delete_url,
        comment
):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        edit_url,
        redirect_detail_comments
):
    """Проверяем, что автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, redirect_detail_comments)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == comment.news
    assert comment.author == comment.author


def test_not_author_cant_edit_comment(not_author_client, comment, edit_url):
    """Проверяем, что пользователь не может изменять чужой комментарий."""
    response = not_author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
