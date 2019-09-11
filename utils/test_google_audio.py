__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

import speech_recognition as sr
import sys
r = sr.Recognizer()
af = sr.AudioFile('test_google_audio.wav')
with af as source:
    my_audio= r.record(source)   
    try:
        my_msg = r.recognize_google(my_audio)
    except:
        print("FAILED to acces Google Cloud Speech-to-Text")
        sys.exit()
    print("SUCCESFULLY accesed Google Cloud Speech-to-Text")
