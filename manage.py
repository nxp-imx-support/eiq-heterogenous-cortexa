#!/usr/bin/env python

__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import os
import sys

from multiprocessing import Manager

if __name__ == '__main__':
    
    from recognizer_multicore import MultiProcessRecognizer, MANAGE

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartDoor.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    MANAGE.manager = Manager()
    MANAGE.face_locations_processed = MANAGE.manager.dict()
    MANAGE.recognition_response = MANAGE.manager.dict()
    MANAGE.thread_list = MANAGE.manager.dict()
    # dict key: 'user_id'; will always keep only one
    # value: the user ID for which the training request
    # is active.
    MANAGE.crt_user_id_to_train = MANAGE.manager.dict()

    MultiProcessRecognizer.return_locator(MANAGE.face_locations_processed, MANAGE.recognition_response,
                                          MANAGE.thread_list, MANAGE.crt_user_id_to_train)
    MultiProcessRecognizer.return_recognizer(MANAGE.face_locations_processed, MANAGE.recognition_response,
                                             MANAGE.thread_list, MANAGE.crt_user_id_to_train)

    execute_from_command_line(sys.argv)
