__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.urls import path
from . import views

urlpatterns = [
    path('key_word_spotting/', views.key_word_spotting, name='kws'),
]