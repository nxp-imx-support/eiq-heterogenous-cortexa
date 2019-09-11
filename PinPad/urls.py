__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.render_pinpad, name='pinpad')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)