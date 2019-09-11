__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import sys
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'SmartDoor'
    verbose_name = 'Smart_Door'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True
