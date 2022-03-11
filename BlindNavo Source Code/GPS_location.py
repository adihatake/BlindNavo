from gps import *
import geopy.distance
import geocoder
import os
import time
from Mic_functs import TextToSpeech, Speak


running = True

os.system("sudo systemctl stop gpsd.socket")
os.system("sudo systemctl disable gpsd.socket")
os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)


def current_location():
        nx = gpsd.next()
        if nx['class'] == 'TPV':
            latitude = getattr(nx,'lat', "Unknown")
            longitude = getattr(nx,'lon', "Unknown")
            print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
            
            return latitude, longitude


def get_difference_CurrentGoal(end_coordinate):   
    while True:
         nx = gpsd.next()
         if nx['class'] == 'TPV':
                 break
    
    if nx['class'] == 'TPV':
            latitude = getattr(nx,'lat', "Unknown")
            longitude = getattr(nx,'lon', "Unknown")
            
    current_coordinate = (latitude, longitude)
    goal_difference = geopy.distance.distance(current_coordinate, end_coordinate).meters
    
    return goal_difference, current_coordinate, end_coordinate



def check_GPS_status():
    while running:
            while True:
                 nx = gpsd.next()
                 if nx['class'] == 'TPV':
                         break
                        
            Speak('/home/pi/Directions_for_the_blind/Audio_Files/GPS.mp3')
            print(nx['class'])
            if nx['class'] == 'TPV':
                latitude = getattr(nx,'lat', "Unknown")
                print(latitude)
                if latitude != "Unknown":
                    print('ready')
                    
                    break

