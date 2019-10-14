__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.http import JsonResponse, HttpResponse
from Recognition.models import ImageDatabase
from Recognition import recognition_common
from recognizer_multicore import MultiProcessRecognizer
from threading import get_ident
import shutil
import os
import subprocess
import cv2
import errno

import logging
# logger config is done in __init__ for each module
logger = logging.getLogger(__name__)

class TemporaryWrapper(object):
    frame_containing_face = []
    frame_face_locations = []

# Create your views here.
def return_recognition(request):
    MultiProcessRecognizer.recognize_request.set()

    MultiProcessRecognizer.can_access_recognition.wait()
    data = MultiProcessRecognizer.return_recognition_response()

    MultiProcessRecognizer.can_access_recognition.clear()

    return JsonResponse(data)

def add_user(request, user_name):
    logging.info("   >>> [add_user]: " + user_name)

    response = dict()
    if (ImageDatabase.objects.filter(name=user_name).exists()):
        logging.info("   >>> [add_user]: user " + user_name + " already exists in database!")
        response['response'] = False
        return JsonResponse(response)

    # Save the new user in the db before data training.
    # The db ID (an unique key) is needed by the
    # opencv recognition algorithm which needs int labels
    # for the images.
    logging.info("   >>> [add_user]: user_name = " + user_name)
    newUserDbEntry = ImageDatabase(name=str(user_name))
    newUserDbEntry.save()

    logging.info("   >>> [imageDatabase.id] id = " + str(newUserDbEntry.id))

    response['user_db_id'] = str(newUserDbEntry.id)
    response['response'] = True

    return JsonResponse(response)

def return_training_folders(dir):
    dirs = [f.path for f in os.scandir(dir) if f.is_dir()]

    return dirs

def take_snapshot(request):
    logging.info("   >>> [take_snapshot]")
    response = dict()
    response['response'] = True

    MultiProcessRecognizer.take_snapshot_request.set()
    MultiProcessRecognizer.can_access_snapshot.wait()
    MultiProcessRecognizer.can_access_snapshot.clear()

    return JsonResponse(response)

def save_snapshot(request, usr_db_id, snapshot_idx):
    logging.info("   >>> [save_snapshot]: user id = " + str(usr_db_id) + "; user_idx = " + str(snapshot_idx))
    response = dict()
    response['response'] = True

    if (snapshot_idx > recognition_common.NUM_TRAIN_SAMPLES):
        print ("   >>> [save_snapshot]: snapshot idx (" + snapshot_idx + ") out of range (max val = " + recognition_common.NUM_TRAIN_SAMPLES + ")")
        response['response'] = False
    else:
        try:
            shutil.copyfile(recognition_common.TMP_SNAPSHOT_ROI_PATH, recognition_common.TRAIN_DATA_PATH + str(usr_db_id) +  '.' + str(snapshot_idx) + ".jpg");
        except shutil.Error as err:
            print (err)
            response['response'] = False

    return JsonResponse(response)

def cancel_adding_user(request, user_id):
    logging.info("   >>> [cancel_adding_user]: " + user_id)
    response = dict()
    response['response'] = True

    # Delete user from DB
    try:
        ImageDatabase.objects.filter(id = user_id).delete()
    except ImageDatabase.DoesNotExist:
        print("   >>> [cancel_adding_user]: Unexpected error occured - user ID " + user_id + " not found in the data base")
        response['response'] = False
    except ImageDatabase.ProtectedError:
        print("   >>> [cancel_adding_user]: Unexpected error occured - entry user ID " + user_id + " cannot be deleted")
        response['response'] = False

    recognition_common.deleteTrainSamplesForId(user_id)

    return JsonResponse(response)

def retrain_new_user(request, user_name, usr_db_id, snapshot_idx):
    logging.info("   >>> [retrain_new_user]: ")
    response = dict()
    response['response'] = True

    try:
        userEntry = ImageDatabase.objects.get(name = user_name)
        logging.info("   >>> [retrain_new_user]: BEFORE trainRecognitionModel")
        response['trainingtime'] = recognition_common.trainRecognitionModel()
        logging.info("   >>> [retrain_new_user]: AFTER trainRecognitionModel")
        # Store picture for new user.
        face_url = recognition_common.SNAPS_PATH + str(usr_db_id) + ".jpg"
        shutil.copyfile(recognition_common.TMP_SNAPSHOT_PATH, face_url);
        relative_face_url = recognition_common.RELATIVE_SNAPS_PATH + str(usr_db_id) + ".jpg"

        userEntry.face = relative_face_url
        userEntry.save()

        response['usersnumber'] = len(ImageDatabase.objects.all())


    except ImageDatabase.DoesNotExist:
        print("   >>> [retrain_new_user]: Unexpected error occured - " + user_name + " not found in the data base")
        response['response'] = False

    return JsonResponse(response)

def sleep(request):
    logging.info("   >>> [sleep] ")
    
    MultiProcessRecognizer.CPU_sleep_request.set()
    # Wait until recognizer_multicore.py face locator process closes the camera 
    MultiProcessRecognizer.CPU_can_sleep.wait()
    
    # Put Cortex-A in low power mode
    f = open("/sys/power/state", "w+")
    f.write("mem")

    # Do not remove 'f.close()'; it is necessary to force the write in order to enter the low power mode
    try:
        f.close()
    except IOError as e:
        if e.errno == errno.EWOULDBLOCK:
            print('/sys/power/state:', os.strerror(errno.EWOULDBLOCK))
    
    logging.info("   >>> [sleep]: done. Send request to re-open the camera")    
    MultiProcessRecognizer.CPU_wake_request.set()

    response = dict()
    response['response'] = True
    return JsonResponse(response)
