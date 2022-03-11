import io, os
import cv2
import pandas as pd
import numpy as np
import time
import sys
import time

from time import sleep
from numpy import random
from typing import List
from object_detector import Detection, ObjectDetector, ObjectDetectorOptions

model = '/home/pi/Downloads/efficientdet_lite0.tflite'
camera_id = 0
width = 640
height = 480
##Model only accepts image sizes for these dimensions

options = ObjectDetectorOptions(
  num_threads=4,
  score_threshold=0.4,
  enable_edgetpu=False)

detector = ObjectDetector(model_path=model, options=options)

def get_centre(bounding):
    centre_x = (bounding[0][0] + bounding[1][0]) / 2
    centre_y = (bounding[0][1] + bounding[1][1]) / 2

    object_centre = [centre_x, centre_y]
    image_centre = [320, 240]
    in_box = False
    
    if bounding[0][0] <= image_centre[0] <= bounding[1][0]:
        if bounding[0][1] <= image_centre[1] <= bounding[1][1]:
                in_box = True
        
    

    return object_centre, image_centre, in_box


def obtain_relevant_objects(
        image: np.ndarray,
        detections: List[Detection],
    ) -> np.ndarray:

      all_nearby_obj = []
      for detection in detections:
        start_point = detection.bounding_box.left, detection.bounding_box.top
        end_point = detection.bounding_box.right, detection.bounding_box.bottom
        bounding_boxes = [start_point, end_point] 

        category = detection.categories[0]
        class_name = category.label
        probability = round(category.score, 2)

        bounding_boxes = [start_point, end_point]
        
        centre_of_object, centre_of_img, in_bbox = get_centre(bounding_boxes)

         
        _MARGIN = 10  
        _ROW_SIZE = 10  
        _FONT_SIZE = 1
        _FONT_THICKNESS = 1


        if in_bbox == True:
            _TEXT_COLOR = (0, 0, 255)
            
           all_nearby_obj.append(class_name)


      return image, all_nearby_obj


def camera_detection():
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Continuously capture images from the camera and run inference
    success, image = cap.read()
    cv2.imwrite('/home/pi/Directions_for_the_blind/objects_detected.jpg', image)
    objects = []
    
    # Run object detection estimation using the model.
    if type(image) != None:
        detections = detector.detect(image)
        image, objects = obtain_relevant_objects(image, detections)

        cap.release()

    return objects
