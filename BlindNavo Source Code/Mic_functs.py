import pyaudio
import wave
import speech_recognition as sr
import os
import time
import gtts
import RPi.GPIO as GPIO
import pygame
from pygame import mixer
from time import sleep
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from mutagen.mp3 import MP3

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 5  # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = '/home/pi/Directions_for_the_blind/Audio_Files/user.wav' # name of .wav file


def Speak(audiofile):
    mixer.init()
    mixer.music.load(audiofile)
    mixer.music.set_volume(0.7)
    mixer.music.play()
    audio = MP3(audiofile)
    letplaySecs = audio.info.length
    time.sleep(letplaySecs + 0.4)
    pygame.quit()

def TextToSpeech(mytext, title):    
    language = 'en'
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save("/home/pi/Directions_for_the_blind/Audio_Files/" + title + ".mp3")
  
def mic_record():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    while True:
        data = stream.read(chunk)
        frames.append(data)
        if GPIO.input(18) == GPIO.HIGH:
            break
        
    GPIO.cleanup()  
    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()


    audio_filename = '/home/pi/Directions_for_the_blind/Audio_Files/user.wav'
    r = sr.Recognizer() 


    with sr.AudioFile(audio_filename) as source:
        # listen for the data (load audio to m\emory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        user_text = r.recognize_google(audio_data)
        #print(user_text)

    return user_text




