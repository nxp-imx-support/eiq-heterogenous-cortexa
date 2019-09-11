__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

"""
WSGI config for SmartDoor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartDoor.settings')

application = get_wsgi_application()
