import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()

def speak(text):
    engine.save_to_file(text, 'static/audio.mp3')
    engine.runAndWait()

def listen():
    r = sr.Recognizer()    
    with sr.Microphone() as source: 
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
        return audio

def understand(filePathToAudio):
    r = sr.Recognizer()    
    with sr.AudioFile(filePathToAudio) as source:
        audio = r.record(source)
    MyText = r.recognize_google(audio)
    MyText = MyText.lower()
    return MyText
