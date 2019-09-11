__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.http import JsonResponse
from Recognition.models import ImageDatabase
from recognizer_multicore import MultiProcessRecognizer

import os
import subprocess

def key_word_spotting(request):
    response = dict()
    try:
        file = open('/dev/eIQDemo_device', 'r')
        response['response'] = file.read()[0]
    except IOError:
        response['response'] = False
    return JsonResponse(response)