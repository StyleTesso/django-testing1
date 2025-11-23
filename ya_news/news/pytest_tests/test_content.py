import pytest
from django.test.client import Client

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db
client = Client()


def test_news_paginate(news_example, home_url):
    """
    Проверяем, что на главной странице выводится не более
    10 записей.
    """
    response = client.get(home_url)
    assert response.context['object_list'].count() == NEWS_COUNT_ON_HOME_PAGE


def test_news_sorting(news_example, client, home_url):
    """
    Проверяем сортировку новостей от самой свежей к самой старой.
    Соблюдая условие - Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_sorting(comments_example, client, news, detail_url):
    """
    Проверяем сортировку комментариев в хронологическом порядке
    В начале списка - старые, в конце - новые.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    all_timestamps = [comment.created
                      for comment
                      in response.context['news'].comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news, detail_url):
    """
    Проверяем, что анонимному пользователю
    недоступна форма для отправки комментария.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, news, detail_url):
    """
    Проверяем, что авторизованному пользователю
    доступна форма для отправки комментария.
    """
    response = not_author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)
