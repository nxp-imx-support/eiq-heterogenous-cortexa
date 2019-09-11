__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import cv2
import os
import glob
from datetime import datetime
import numpy as np
import logging
import time

# logger config is done in __init__ for each module
logger = logging.getLogger(__name__)

CRT_PATH = os.path.dirname(os.path.abspath(__file__))

TRAIN_FOLDER = "train/"
MEDIA_FOLDER = "../media"
TRAIN_DATA_PATH = os.path.join(CRT_PATH, MEDIA_FOLDER, TRAIN_FOLDER)
SNAPS_PATH = os.path.join(CRT_PATH,  MEDIA_FOLDER, "snaps/")
RELATIVE_SNAPS_PATH = 'snaps/'
TIMESTAMPS_FOLDER = "timestamps/"
TIMESTAMPS_PATH = os.path.join(CRT_PATH,  MEDIA_FOLDER, TIMESTAMPS_FOLDER)
MODELS_PATH = os.path.join(CRT_PATH, "../models/")
RECOGNITION_MODEL_PATH = os.path.join(CRT_PATH, "../models/face_recognizer.yml")
TMP_SNAPSHOT_PATH = os.path.join(CRT_PATH,  MEDIA_FOLDER, "tmp_snapshot.jpg") # Keep in sync with TMP_SNAPSHOT_PATH from static/dashboard.js
TMP_SNAPSHOT_ROI_PATH = os.path.join(CRT_PATH,  MEDIA_FOLDER, "tmp_snapshot_roi.jpg") # Keep in sync with TMP_SNAPSHOT_ROI_PATH from static/dashboard.js

IMG_SCALING_FACTOR = 1.5

# No of face samples for each user, to use for training
NUM_TRAIN_SAMPLES = 8 # Keep in sync with MAX_NUM_SNAPSHOTS from static/dashboard.js
RECOGNITION_MAX_DELTA = 100 # max accepted error


def cv_size(img):
    return tuple(img.shape[1::-1])

def getTimestampFromDatetime(datetimeToConvert):
    """
    Converts a datetime object to a string by concatenating year, month, day, hour, minute, second.
    @param datetimeToConvert the datetime object to convert
    @return the string corresponding to the given datetime
    """
    logging.info("   >>> [getTimestampFromDatetime] datetimeToConvert: " + str(datetimeToConvert))
    return "%s%s%s%s%s%s" % (datetimeToConvert.year, datetimeToConvert.month, datetimeToConvert.day, datetimeToConvert.hour, datetimeToConvert.minute, datetimeToConvert.second)

def deleteTrainSamplesForId(id):
    idStr = str(id)
    logging.info("   >>> [deleteTrainSamplesForId]: id = " + str(idStr))
    filesToDeleteNamePattern = os.path.join(TRAIN_DATA_PATH, idStr + ".*")
    logging.info("   >>> [deleteTrainSamplesForId]: filesToDeleteNamePattern = " + filesToDeleteNamePattern)
    file_names = glob.glob(filesToDeleteNamePattern)
    logging.info("   >>> [deleteTrainSamplesForId]: " + str(file_names))
    logging.info("   >>> [deleteTrainSamplesForId]: Deleting " + str(len(file_names)) + " image samples!")
    for file in file_names:
        os.remove(file)

def deleteSnapForId(id):
    idStr = str(id)
    logging.info("   >>> [deleteSnapForId]: id = " + str(idStr))
    fileToDelete = os.path.join(SNAPS_PATH, idStr + ".jpg")
    logging.info("   >>> [deleteSnapForId]: fileToDelete = " + fileToDelete)
    os.remove(fileToDelete)

def deleteLogsForTimestamp(logEntryTimestamp):
    """
    Deletes the picture associated with the given timestamp from the media/timestamps folder.
    @param logEntryTimestamp the timestamp associated with a Logs Database entry. Expected to be a datetime.datetime object.
    """
    logging.info("   >>> [deleteLogsForTimestamp] logEntryTimestamp: " + logEntryTimestamp)
    fileToDelete = os.path.join(TIMESTAMPS_PATH, logEntryTimestamp + ".jpg")
    logging.info("   >>> [deleteLogsForTimestamp]: filesToDeleteNamePattern = " + fileToDelete)
    os.remove(fileToDelete)

def clearRecognitionModel():
    if (os.path.exists(RECOGNITION_MODEL_PATH)):
        os.remove(RECOGNITION_MODEL_PATH)

def trainRecognitionModel():
    tmpRecognizer = cv2.face.LBPHFaceRecognizer_create()

    faces, labels = getUsersImagesAndLabels()
    logging.info("   >>> [trainRecognitionModel]: labels = " + str(labels))

    # (Re) train face recognizer.
    logging.info("   >>> [trainRecognitionModel]: tmpRecognizer.train")
    start = time.time()
    tmpRecognizer.train(faces, np.array(labels))
    end = time.time()

    # Save the model into trainer/trainer.yml
    logging.info("   >>> [trainRecognitionModel]: tmpRecognizer.write")
    tmpRecognizer.write(RECOGNITION_MODEL_PATH)
    logging.info("   >>> [trainRecognitionModel]: trained model is here: " + RECOGNITION_MODEL_PATH)

    return str(round((end - start) * 1000, 3)) + ' ms'

def getUsersImagesAndLabels():

    imagePaths = [os.path.join(TRAIN_DATA_PATH,f) for f in os.listdir(TRAIN_DATA_PATH)]
    faceSamples=[]
    labels = []

    for imagePath in imagePaths:
        gray_roi = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
        cv_size(gray_roi)

        id = int(os.path.split(imagePath)[-1].split(".")[0])
        labels.append(id)
        faceSamples.append(gray_roi)
    return faceSamples, labels
