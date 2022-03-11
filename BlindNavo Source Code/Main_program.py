import Mic_functs
import camera_EfficientNet
import os
import googlemaps
import re
import geopy.distance as gd
import time
import RPi.GPIO as GPIO
import GPS_location
import voice_functions
import multiprocessing
import segment_img
import os

from gps import *
from segment_img import get_scores
from voice_functions import ask_directions, say_objects
from Mic_functs import Speak, TextToSpeech, mic_record
from camera_EfficientNet import camera_detection
from GPS_location import get_difference_CurrentGoal, current_location, check_GPS_status
from datetime import datetime

os.system("sudo systemctl stop gpsd.socket")
os.system("sudo systemctl disable gpsd.socket")
os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)



def camera_process(queue):
    prev_object_list = []
    text_to_say = []
    increment = 0
    
    while True:
        current_objects_detected = camera_detection()
        
        for items in current_objects_detected:
            if items not in prev_object_list:     
                 text_to_say.append(items)
                 prev_object_list.append(items)

        queue.put(text_to_say)

        text_to_say = []
              
        if increment == 10:
              prev_object_list = []
              increment = 0

        increment += 1
        

def check_button(button_event):
    while True:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        if GPIO.input(18) == GPIO.HIGH:
            button_event.set()

        GPIO.cleanup()
        

def segment_process(queue):
    prev_segment_list = []
    
    while True:
        recommendation = get_scores()

        queue.put(recommendation)


def gps(gps_event, queue, end_Coords):
    while True:
        start_time = time.time()
        while True:
            difference_from_Goal, location, goal_coord = get_difference_CurrentGoal(end_Coords)
            
            difference_from_Goal = difference_from_Goal // 3.281
            difference_from_Goal = int(difference_from_Goal)
            
            if difference_from_Goal <= 15:
                          gps_event.set()


            if (time.time() - start_time) > 9:
                    
                    if difference_from_Goal > 15:
                          attention = 'Continue for ' + str(difference_from_Goal) + ' steps'
                          TextToSpeech(attention, 'attention')
                          message = 'GPS continue'
                          queue.put(message)
                          break


def speak_queue(queue):
    while True:
        while not queue.empty():
            order = queue.get()
      
            if order == 'Slight left':
                while not queue.empty():
                    queue.get()
                Speak('/home/pi/Directions_for_the_blind/Audio_Files/slight left.mp3')
                    
            if order == 'Slight right':
                while not queue.empty():
                    queue.get()
                Speak('/home/pi/Directions_for_the_blind/Audio_Files/slight right.mp3')


            
            if len(order) >= 1:
                if order != 'Slight left':
                    if order != 'Slight right':
                        if order != 'Continue straight':
                            if order != 'GPS continue':                           
                                say_objects(order)
                                while not queue.empty():
                                    queue.get()


            if order == 'GPS continue':
                while not queue.empty():
                            queue.get()
                Speak('/home/pi/Directions_for_the_blind/Audio_Files/attention.mp3')
                  



def main():
    while True:
        Main_Running = True
        while Main_Running:
            gmaps = googlemaps.Client(key='AIzaSyBfReYXRLdOuFlYBURwaJxpyjuH1jYevP8')
            Running = 1
            
            while Running <= 1:
                Speak('/home/pi/Directions_for_the_blind/Audio_Files/start.mp3')
                NotPressed = True
                
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                
                while NotPressed:
                    if GPIO.input(18) == GPIO.HIGH:
                        NotPressed = False
                confirmation_user, destination = ask_directions()
                
                if confirmation_user == False:
                    Running += 1

                GPIO.cleanup()


            while True:
                 nx = gpsd.next()
                 if nx['class'] == 'TPV':
                         break
            
            if nx['class'] == 'TPV':
                    lat= getattr(nx,'lat', "Unknown")
                    long = getattr(nx,'lon', "Unknown")
                    
            lat = str(lat)
            long = str(long)
            location = lat + ', ' + long
            directions_result = gmaps.directions(location,
                                                 str(destination),
                                                 mode="walking")


            directions = directions_result[0]
            directions_1 = []

            for key, value in directions.items():
                directions_1.append(value)

            directions_1 = list(directions_1)
            #switch to [6][0] if using python 2.7
            #switch to [2][0] for python 3
            directions_2 = directions_1[2][0]
            directions_3 = []

            for key, value in directions_2.items():
                directions_3.append(value)


            all_directions = []

            for each_direct in directions_3[6]:
              all_directions.append(each_direct)


            num_of_steps = len(all_directions)


            for i in range(num_of_steps):
                  if Main_Running == False:
                      break
                    
                  one_direction = all_directions[i]
                  Step_Distance = []
                  Step_Duration = []
                  Step_Instructions = []
                  Step_start_coordinate = []
                  Step_end_coordinate = []

                  distance = one_direction.get("distance")
                  duration = one_direction.get("duration")
                  instructions = str(one_direction.get("html_instructions"))
                  start_coordinate = one_direction.get("start_location")
                  end_coordinate = one_direction.get("end_location")


                  for key, value in distance.items():
                      Step_Distance.append(value)

                  for key, value in duration.items():
                      Step_Duration.append(value)

                  for key, value in end_coordinate.items():
                      Step_end_coordinate.append(value)

                  for key, value in start_coordinate.items():
                      Step_start_coordinate.append(value)

                  TAG_RE = re.compile(r'<[^>]+>')

                  instructions = TAG_RE.sub('', instructions)

                  Step_Instructions.append(instructions)  

                  start_coords = (Step_start_coordinate[0], Step_start_coordinate[1])
                  end_coords = (Step_end_coordinate[0], Step_end_coordinate[1])

                  #meters_from_next_Step = gd.distance(start_coords, end_coords).meters
                  unedited_step = Step_Instructions[0]
                  
                  step = Step_Instructions[0]
                  step = str(step)
                  
                  step_distance = int(Step_Distance[1]) // 3.281
                  step_distance = int(step_distance)
                  step_distance = str(step_distance)

          
                  if 'Head' in step:
                        step = step + ' for ' + step_distance + ' steps.'
        
                  if 'Turn' in step:
                        step = step + ' and continue straight for ' + step_distance + 'steps'
            
                  
                  TextToSpeech(mytext=step, title="direction")
                  Speak('/home/pi/Directions_for_the_blind/Audio_Files/direction.mp3')

                  prev_object_list = []
                  increment = 0
                  
                  jobs = []

                  gps_event = multiprocessing.Event()
                  button_event = multiprocessing.Event()
                  queue = multiprocessing.Queue()

                  button_checker = multiprocessing.Process(target=check_button,args=(button_event,))
                  jobs.append(button_checker)
                  button_checker.start()

                  gps_check = multiprocessing.Process(target=gps,args=(gps_event, queue, end_coords))
                  jobs.append(gps_check)
                  gps_check.start()

                  cam_p = multiprocessing.Process(target=camera_process,args=(queue,))
                  jobs.append(cam_p)
                  cam_p.start()

                  segment_p = multiprocessing.Process(target=segment_process,args=(queue,))
                  jobs.append(segment_p)
                  segment_p.start()

                  speaking_queue = multiprocessing.Process(target=speak_queue,args=(queue,))
                  jobs.append(speaking_queue)
                  speaking_queue.start()


                  running = True

                  while running:
                      if button_event.is_set():
                          for all_jobs in jobs:
                              all_jobs.terminate()
                              Main_Running = False
                              running = False
                
                          break
                        
                      if len(jobs) > 0:          
                          if gps_event.is_set():
                              for all_jobs in jobs:
                                  all_jobs.terminate()
                                  running = False
                              break

        if Main_Running == True:
               arrive = 'You have arrived'
               TextToSpeech(mytext=arrive, title="arrival")
               Speak('/home/pi/Directions_for_the_blind/Audio_Files/arrival.mp3')


                          

                          

if __name__ == "__main__":
    check_GPS_status()
    main()
