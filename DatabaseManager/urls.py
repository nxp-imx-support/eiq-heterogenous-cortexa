__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.return_logs, name='logs'),
    path('users/', views.get_active_users, name='users'),
    path('user/id/<user_id>', views.return_user_info_id, name='user_id'),
    path('user/name/<user_name>', views.return_user_info_name, name='user_name'),
]