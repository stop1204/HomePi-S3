# pip install SpeechRecognition
# https://pypi.org/project/SpeechRecognition/
import speech_recognition as sr
from os import path
r = sr.Recognizer()
print(sr.Microphone.list_microphone_names())

r.energy_threshold = 4000
r.pause_threshold = 0.8


AUDIO_FILE_EN = path.join(path.dirname(path.realpath(__file__)), "/Users/terry/Desktop/New Recording.wav")
with sr.AudioFile(AUDIO_FILE_EN) as source:
    audio_en = r.record(source)  # read the entire audio file
    print("AUDIO said: " + r.recognize_sphinx(audio_en))

with sr.Microphone() as source:
    print("Say something!")
    keywords = [("hello", 0.8), ("world", 0.8)]
    r.adjust_for_ambient_noise(source) # decrease noise
    audio = r.listen(source)
    try:
        # online API
        # print("You said: " + r.recognize_goog`le(audio))
        # offline API
        # print("You said: " + r.recognize_sphinx(audio,keyword_entries=keywords))
        print("You said: " + r.recognize_sphinx(audio))
        print("You said: " + r.recognize_sphinx(AUDIO_FILE_EN))

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Error; {0}".format(e))
