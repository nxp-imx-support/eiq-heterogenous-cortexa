__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.urls import path
from . import views

urlpatterns = [
    path('', views.return_recognition, name='recog'),
    path('add_user/<user_name>/', views.add_user, name='add_user'),
    path('take_snapshot/', views.take_snapshot, name='take_snapshot'),
    path('save_snapshot/<int:usr_db_id>/<int:snapshot_idx>/', views.save_snapshot, name='save_snapshot'),
    path('cancel_adding_user/<user_id>', views.cancel_adding_user, name='cancel_adding_user'),
    path('retrain_new_user/<str:user_name>/<int:usr_db_id>/<int:snapshot_idx>/', views.retrain_new_user, name='retrain_new_user'),
    path('sleep/', views.sleep, name='sleep'),
]