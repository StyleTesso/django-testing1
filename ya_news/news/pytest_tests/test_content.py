import pytest
from django.test.client import Client

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db
client = Client()


def test_paginate(all_news, home_url):
    """Проверяем, что на главную страницу выводится не более 10 записей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == NEWS_COUNT_ON_HOME_PAGE


def test_news_sorting(all_news, client, home_url):
    """
    Проверяем сортировку новостей от самой свежей к самой старой.
    Соблюдая условие - Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_sorting(all_comments, client, detail_url):
    """Проверяем, сортировку комментариев в хронологическом порядке."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, detail_url):
    """
    Проверяем, что анонимному пользователю
    недоступна форма для отправки комментария.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(reader_client, news, detail_url):
    """
    Проверяем, что авторизованному пользователю
    доступна форма для отправки комментария.
    """
    response = reader_client.get(detail_url)
    assert 'form' in response.context
