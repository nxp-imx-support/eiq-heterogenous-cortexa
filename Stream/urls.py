__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.urls import path
from . import views

urlpatterns = [
    path('', views.return_stream, name='stream'),
    path('generate', views.generate_stream, name='generate'),
]