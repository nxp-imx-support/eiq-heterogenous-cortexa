__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import django
from django.db import connection
import os
from timeit import default_timer as timer
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartDoor.settings')
django.setup()

from Recognition.models import ImageDatabase, LogsDatabase
import multiprocessing as mp
from multiprocessing import Lock, Manager, Process, JoinableQueue, Event

import cv2
import time
import timeit
import platform
from Recognition import recognition_common

import logging
# logger config is done in __init__ for each module
logger = logging.getLogger(__name__)


# FACE DETECTION
# Used as reference: https://www.hackster.io/mjrobot/real-time-face-recognition-an-end-to-end-project-a10826

# https://github.com/Itseez/opencv/tree/master/data/haarcascades
haarCascade = cv2.CascadeClassifier(os.path.join(recognition_common.MODELS_PATH, 'haarcascade_frontalface_default.xml'))

# https://github.com/opencv/opencv/tree/master/data/lbpcascades
lbpCascade = cv2.CascadeClassifier(os.path.join(recognition_common.MODELS_PATH, 'lbpcascade_frontalface_improved.xml'))

# LBP is faster that HAAR, but less accurate. Confirmed for this app - the speed is much
# better, while the loss in accuracy is not noticeable.
FACE_CASCADE_MODEL = lbpCascade

def db_table_exists(table_name):
    return table_name in connection.introspection.table_names()
        
class WorkerProcess(Process):
    def __init__(self, name, thread_list, faces_toberecognized, face_locations_processed, recognition_response,
                 recognize_request, can_recognize, can_access_recognition, recognition_lock,
                 train_data_request, can_access_train_data, take_snapshot_request, can_access_snapshot, CPU_sleep_request, CPU_wake_request, CPU_can_sleep, crt_user_id_to_train):
        super().__init__()
        self.name = name
        self.thread_list = thread_list
        self.faces_toberecognized = faces_toberecognized
        self.recognize_request = recognize_request
        self.can_recognize = can_recognize
        self.face_locations_processed = face_locations_processed
        self.recognition_response = recognition_response
        self.can_access_recognition = can_access_recognition
        self.recognition_lock = recognition_lock
        self.train_data_request = train_data_request
        self.can_access_train_data = can_access_train_data
        self.crt_user_id_to_train = crt_user_id_to_train
        self.take_snapshot_request = take_snapshot_request
        self.can_access_snapshot = can_access_snapshot
        self.CPU_sleep_request = CPU_sleep_request
        self.CPU_wake_request = CPU_wake_request
        self.CPU_can_sleep = CPU_can_sleep
        
        if not os.path.exists(recognition_common.TRAIN_DATA_PATH):
            os.makedirs(recognition_common.TRAIN_DATA_PATH)
        if not os.path.exists(recognition_common.SNAPS_PATH):
            os.makedirs(recognition_common.SNAPS_PATH)
   
    def recognize(self, face_img_tuple):
        """Predicts face identity for the input image.
        The input image is expected to contain only one face.
        
        @type face_img_tuple: a tuple (img, img)
        @param rois: The input image - tuple containg the color ROI (region of interest)
                     and a full snapshot of the face(region of interest)
        
        @rtype dict
        @returns: A dictionary describing the identity.
                  Keys: 'identity', 'response'
                  Key 'identity' can be associated with one of three string values:
                     ERROR - no face detected
                     Unknown - detected face not recognized
                     <user_name> - the name of the user whose face was recognized
                  Key 'response' is associated with a bool value:
                     True: if the face was succesfully recognized.
                     False: if the face was not recognized.

        """
        return_val_dict = dict()
        return_val_dict['inftime']  = '0.000 ms'
        return_val_dict['identity'] = 'Unknown'
        return_val_dict['response'] = 'False'

        color_roi, full_face_snapshot = face_img_tuple

        # Re-create recognizer each time. Because the database can change (users added or deleted), if
        # the same instance of a recognizer is created it seems to get corrupted and fails to predict correctly. 
        FACE_RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()       

        timestamp = datetime.now()
        time_stamp_str = recognition_common.getTimestampFromDatetime(timestamp)
        log_entry = LogsDatabase()                
        log_entry.timestamp = time_stamp_str
        logging.info("   >>> [recognize] timestamp: " + time_stamp_str) 
        log_entry.face = recognition_common.TIMESTAMPS_FOLDER + time_stamp_str + '.jpg'
        log_entry.save()
        # also store the images to disk
              
        tbs_log_path = recognition_common.TIMESTAMPS_PATH + time_stamp_str + '.jpg'
        logging.info("   >>> [recognize] log path = " + tbs_log_path)
        cv2.imwrite(tbs_log_path, full_face_snapshot)
       
        if (not db_table_exists(ImageDatabase._meta.db_table)):
            logging.info("   >>> [recognize]: ImageDatabase does not exist!")
            return return_val_dict
        
        all_entries = ImageDatabase.objects.all()
        if (not all_entries.exists()):
            logging.info("   >>> [recognize]: Empty ImageDatabase!")
            return return_val_dict
        
        if (not os.path.exists(recognition_common.RECOGNITION_MODEL_PATH)):
            recognition_common.trainRecognitionModel()

        try:
            logging.info("   >>> [recognize]: FACE_RECOGNIZER.read")
            FACE_RECOGNIZER.read(recognition_common.RECOGNITION_MODEL_PATH)
        except cv2.error as e:
            print("   >>> [recognize]: ERROR LOADING MODEL: " + str(e))
            return return_val_dict            
        
           
        gray_roi_to_recognize = cv2.cvtColor(color_roi, cv2.COLOR_BGR2GRAY)

        start = time.time()
        logging.info("   >>> [recognize]: FACE_RECOGNIZER.predict")
        label, delta = FACE_RECOGNIZER.predict(gray_roi_to_recognize)
        end = time.time()
        logging.info("   >>> [recognize]: time = " + str(end - start))
        logging.info("   >>> [recognize]: label = " + str(label))
        logging.info("   >>> [recognize]: diff = " + str(delta))
        
        return_val_dict['inftime'] = str(round((end - start) * 1000, 3)) + ' ms'
        
        if (delta >= recognition_common.RECOGNITION_MAX_DELTA):
            # Low confidence of accurate recognition.
            # Returns Unknown user
            return return_val_dict
        
        try:
            entry = ImageDatabase.objects.get(pk = label)
        except ImageDatabase.DoesNotExist:
            print("   >>> [recognize]: LABEL " + str(label) + " not in data base!\n")
            return return_val_dict
        except ValueError as e:
            print("   >>> [recognize]: LABEL " + str(label) + " not in data base!\n" + str(e))
            return return_val_dict
        id_name = str(entry.name)
        logging.info("   >>> [recognize]: id_name = " + id_name)
        return_val_dict['identity'] = id_name
        return_val_dict['response'] = True
        
        # update log entry with user info
        log_entry.known = True
        log_entry.name = id_name
        log_entry.save()
                
        return return_val_dict
    
    def get_big_rois(self, small_rois):
        big_rois = []
        X_BIG = 0; Y_BIG = 0; W_BIG = 0; H_BIG = 0
        if (len(small_rois) > 0):
            X_BIG = int(small_rois[0][0] * recognition_common.IMG_SCALING_FACTOR)
            Y_BIG = int(small_rois[0][1] * recognition_common.IMG_SCALING_FACTOR)
            W_BIG = int(small_rois[0][2] * recognition_common.IMG_SCALING_FACTOR)
            H_BIG = int(small_rois[0][3] * recognition_common.IMG_SCALING_FACTOR)
            big_rois.append((X_BIG, Y_BIG, W_BIG, H_BIG))
        return big_rois
    
    def check_low_power_state(self, camera):
        """
            Check if there is a request to put Cortex-A in low power state.
            If yes, close the camera to be able to suspend the CPU gracefully.
            When Cortex-A is awakens resume camera.
            @param camera: VideoCapture object associated with the camera on the board.
        """
        if (self.CPU_sleep_request.is_set()):
            if camera.isOpened():                    
                logging.debug("   >>> [check_low_power_state]: Got CPU sleep request. Closing active camera.")
                camera.release()
            self.CPU_sleep_request.clear()
            self.CPU_can_sleep.set()
            logging.debug("   >>> [check_low_power_state]: Waiting for CPU wake request")
            self.CPU_wake_request.wait()
            logging.debug("   >>> [check_low_power_state]: Got CPU wake request. Re-opening camera")
            if (platform.system() == 'Windows'):
                camera.open(0)
            else:
                camera.open("autovideosrc ! video/x-raw,width=640,height=480 ! autovideoconvert ! appsink") # command for board           
            self.CPU_wake_request.clear()
            
    def run_face_locator(self):
        if (platform.system() == 'Windows'):
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture("autovideosrc ! video/x-raw,width=640,height=480 ! autovideoconvert ! appsink") # command for board
        crt_num_train_samples = 1
        
        while True:
            
            self.check_low_power_state(camera)
            
            ret, orig_frame = camera.read()            
            orig_frame = cv2.flip(orig_frame, 1)
            if (ret == False):
                print ('   >>> [run_face_locator]: ERROR reading from the camera')
                break
            
            small_frame = cv2.resize(orig_frame, (0,0), fx=1.0/recognition_common.IMG_SCALING_FACTOR, fy=1.0/recognition_common.IMG_SCALING_FACTOR) 
            
            img_gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            rois = FACE_CASCADE_MODEL.detectMultiScale(img_gray, scaleFactor = 1.4, minNeighbors = 3, minSize = (30,30))
            
            big_rois = self.get_big_rois(rois)

            for thread_identity, _ in self.thread_list.items():
                self.face_locations_processed[thread_identity] = (orig_frame, big_rois)
            
            if (len(rois) == 0):
                continue
                
            (X, Y, W, H) = rois[0] #taking into consideration just one face!
            roi_gray = img_gray[Y : (Y + H), X : (X + W)]
            roi_color = small_frame[Y : (Y + H), X : (X + W)]
            
            if self.recognize_request.is_set():
                print('   >>> [run_face_locator]: Appended ROI to be recognized')
                self.faces_toberecognized.put((roi_color, small_frame))
                self.can_recognize.set()
                self.recognize_request.clear()
                
            if self.take_snapshot_request.is_set():
                self.take_snapshot_request.clear()
                print('   >>> [run_face_locator]: Save tmp snapshot to ', recognition_common.TMP_SNAPSHOT_PATH)
		
                # Resizing snapshot to (64, 64)
                roi_color = cv2.resize(roi_color, (64, 64), interpolation = cv2.INTER_AREA)
                
                cv2.imwrite(recognition_common.TMP_SNAPSHOT_PATH, orig_frame)
                cv2.imwrite(recognition_common.TMP_SNAPSHOT_ROI_PATH, roi_color)
                self.can_access_snapshot.set()           

            if self.train_data_request.is_set():
                if (crt_num_train_samples > recognition_common.NUM_TRAIN_SAMPLES):
                    # Save user picture in database.
                    
                    crt_num_train_samples = 1
                    self.train_data_request.clear()
                    print('   >>> [run_face_locator]: got all data for training')
                    self.can_access_train_data.set()
                else:
                    # Save the captured image into the datasets folder
                    print("   >>> [run_face_locator]: train sample " + str(crt_num_train_samples))                    
                    cv2.imwrite(recognition_common.TRAIN_DATA_PATH + str(self.crt_user_id_to_train['user_id']) +  '.' + str(crt_num_train_samples) + ".jpg", roi_color)
                    (H, W) = recognition_common.cv_size(roi_gray)
                    print ("   >>> [run_face_locator]: H, W: ", H, W)
                    crt_num_train_samples += 1
    
    def run_face_recognizer(self):
        while True:
            self.can_recognize.wait()

            identity = self.recognize(self.faces_toberecognized.get())
            self.recognize_request.clear()
            self.can_recognize.clear()

            self.recognition_response['identity'] = identity

            self.can_access_recognition.set()   
    
    def run(self):
        print('   >>> [run]: {} process started'.format(self.name))

        if self.name == 'locator':
            self.run_face_locator()                                           
        elif self.name == 'recognizer':
            self.run_face_recognizer()


class MultiProcessRecognizer(object):
    workers = []

    locations_lock = Lock()
    recognition_lock = Lock()
   
    recognize_request = Event()
    can_recognize = Event()
    can_access_recognition = Event()
    
    train_data_request = Event()
    can_access_train_data = Event()

    take_snapshot_request = Event()
    can_access_snapshot = Event()

    CPU_sleep_request = Event()
    CPU_wake_request = Event()
    CPU_can_sleep = Event()

    fetched_frames = JoinableQueue()
    faces_toberecognized = JoinableQueue()

    @staticmethod
    def return_face_locations(identity):
        with MultiProcessRecognizer.locations_lock:
            if identity < 0:                
                return MANAGE.face_locations_processed.values()[0]
            return MANAGE.face_locations_processed[identity]

    @staticmethod
    def return_recognition_response():
        with MultiProcessRecognizer.recognition_lock:
            return MANAGE.recognition_response['identity']

    @staticmethod
    def return_locator(face_locations_processed, recognition_response, thread_list, crt_user_id_to_train):
        return WorkerProcess('locator', thread_list, MultiProcessRecognizer.faces_toberecognized,
                             face_locations_processed,
                             recognition_response,
                             MultiProcessRecognizer.recognize_request,
                             MultiProcessRecognizer.can_recognize,
                             MultiProcessRecognizer.can_access_recognition,
                             MultiProcessRecognizer.recognition_lock,
                             MultiProcessRecognizer.train_data_request,
                             MultiProcessRecognizer.can_access_train_data,
                             MultiProcessRecognizer.take_snapshot_request,
                             MultiProcessRecognizer.can_access_snapshot,
                             MultiProcessRecognizer.CPU_sleep_request,
                             MultiProcessRecognizer.CPU_wake_request,
                             MultiProcessRecognizer.CPU_can_sleep,
                             crt_user_id_to_train).start()

    @staticmethod
    def return_recognizer(face_locations_processed, recognition_response, thread_list, crt_user_id_to_train):
        return WorkerProcess('recognizer', thread_list, MultiProcessRecognizer.faces_toberecognized,
                             face_locations_processed,
                             recognition_response,
                             MultiProcessRecognizer.recognize_request,
                             MultiProcessRecognizer.can_recognize,
                             MultiProcessRecognizer.can_access_recognition,
                             MultiProcessRecognizer.recognition_lock,
                             MultiProcessRecognizer.train_data_request,
                             MultiProcessRecognizer.can_access_train_data,
                             MultiProcessRecognizer.take_snapshot_request,
                             MultiProcessRecognizer.can_access_snapshot,
                             MultiProcessRecognizer.CPU_sleep_request,
                             MultiProcessRecognizer.CPU_wake_request,   
                             MultiProcessRecognizer.CPU_can_sleep,                             
                             crt_user_id_to_train).start()

    @staticmethod
    def add_client_thread_identity(identity):
        print("   >>> [add_client_thread_identity]: identity = " + str(identity))
        if not identity in MANAGE.thread_list:
            MANAGE.thread_list[identity] = 1
        print("   >>> [add_client_thread_identity]: thread_list = " + str(MANAGE.thread_list))

    @staticmethod
    # Will be called only once per training session from
    # Recognizer/views.py#add_user()
    # Don't expect to have training requests for different users
    # from multiple threads.
    def set_crt_user_id_for_training(user_id):
        print("   >>> [set_crt_user_id_for_training]: user_id = " + str(user_id))
        MANAGE.crt_user_id_to_train['user_id'] = user_id
        print ("[set_crt_user_id_for_training] MANAGE.crt_user_id_to_train=" + str(MANAGE.crt_user_id_to_train))
        
    
    @staticmethod    
    def get_new_user_id():
        print ("[get_new_user_id] MANAGE.crt_user_id_to_train=" + str(MANAGE.crt_user_id_to_train))
        return MANAGE.crt_user_id_to_train['user_id']
    
class MANAGE(object):
    # Will be initialized in manage.py
    
    manager = None
    face_locations_processed = None
    recognition_response = None
    thread_list = None
    crt_user_id_to_train = None
