__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from recognizer_multicore import MultiProcessRecognizer
from Recognition import recognition_common

import cv2
from threading import get_ident

import time


# from https://stackoverflow.com/questions/46036477/drawing-fancy-rectangle-around-face
def draw_border(img, pt1, pt2, color, thickness, radius, seg_len):
    
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + radius, y1), (x1 + radius + seg_len, y1), color, thickness)
    cv2.line(img, (x1, y1 + radius), (x1, y1 + radius + seg_len), color, thickness)
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - radius, y1), (x2 - radius - seg_len, y1), color, thickness)
    cv2.line(img, (x2, y1 + radius), (x2, y1 + radius + seg_len), color, thickness)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + radius, y2), (x1 + radius + seg_len, y2), color, thickness)
    cv2.line(img, (x1, y2 - radius), (x1, y2 - radius - seg_len), color, thickness)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - radius, y2), (x2 - radius - seg_len, y2), color, thickness)
    cv2.line(img, (x2, y2 - radius), (x2, y2 - radius - seg_len), color, thickness)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

def gen():
    identity = get_ident()
    print ("   >>> [gen]: " + str(identity))
    MultiProcessRecognizer.add_client_thread_identity(identity)

    while True:
        face_locations = []
        frame = []
        try:
            frame, face_locations = MultiProcessRecognizer.return_face_locations(identity)
        except:
            pass        
        if not frame == []:           
            if (len(face_locations) > 0):
                for (X, Y, W, H) in face_locations:
                    draw_border(frame,
                            (X , Y),
                            (X + W, Y + H),
                            (0, 255, 0),
                            2, 
                            15,
                            20)                  

            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Create your views here.
@gzip.gzip_page
def generate_stream(request):
    return StreamingHttpResponse(streaming_content=gen(), content_type='multipart/x-mixed-replace; boundary=frame')

def return_stream(request):
    return render(request, 'stream.html')