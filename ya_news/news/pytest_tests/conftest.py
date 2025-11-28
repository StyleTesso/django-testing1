from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Заголовок',
        text='Текст',
    )


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def comment(author, news, db):
    return Comment.objects.create(
        news=news,
        text='Текст',
        author=author
    )


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def all_news(db):
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=datetime.today() - timedelta(days=index)
        )for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def all_comments(author, news, db, detail_url):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария{index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


@pytest.fixture
def redirect_detail_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def redirect_login_url(detail_url, login_url):
    return f'{login_url}?next={detail_url}'
