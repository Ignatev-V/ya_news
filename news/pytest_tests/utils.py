"""Общие константы для тестов."""
from django.urls import reverse

NEWS_HOME = reverse('news:home')
NEWS_DELETE_URL = 'news:delete'
NEWS_EDIT_URL = 'news:edit'
NEWS_DETAIL_URL = 'news:detail'
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
