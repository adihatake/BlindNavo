import argparse
import sys
import time
import math
from typing import List

import cv2
import PIL
from image_segmenter import ColoredLabel
from image_segmenter import ImageSegmenter
from image_segmenter import ImageSegmenterOptions
from PIL import Image
import numpy as np
import segment_utils

# Visualization parameters
_LEGEND_TEXT_COLOR = (0, 0, 255)  # red
_LEGEND_BACKGROUND_COLOR = (255, 255, 255)  # white
_LEGEND_FONT_SIZE = 1
_LEGEND_FONT_THICKNESS = 1
_LEGEND_ROW_SIZE = 20  # pixels
_LEGEND_RECT_SIZE = 16  # pixels
_LABEL_MARGIN = 10
_PADDING_WIDTH_FOR_LEGEND = 150  # pixels

camera_id = 0
width = 640
height = 480
threshold = 5
img_height_width = 100

model = '/home/pi/Directions_for_the_blind/lite-model_deeplabv3-mobilenetv2-ade20k_1_default_2.tflite'

options = ImageSegmenterOptions(
    num_threads=4, enable_edgetpu=False)

segmenter = ImageSegmenter(model_path=model, options=options)

start_time = time.time()

def segment_run():

  image = cv2.imread('/home/pi/Directions_for_the_blind/objects_detected.jpg')

  # Segment with each frame from camera.
  if type(image) != None:
    segmentation_result = segmenter.segment(image)

    # Convert the segmentation result into an image.
    seg_map_img, found_colored_labels = segment_utils.segmentation_map_to_image(
    segmentation_result)


    # Resize the segmentation mask to be the same shape as input image.
    seg_map_img = cv2.resize(
    seg_map_img,
    dsize=(image.shape[1], image.shape[0]),
    interpolation=cv2.INTER_NEAREST)

    # Visualize segmentation result on image.
    display_mode = 'overlay'
    overlay = seg_map_img

    for colored_label in found_colored_labels:
      rect_color = colored_label.color

    cv2.imwrite('/home/pi/Directions_for_the_blind/segmentation_out.jpeg', overlay)




def create_intervals():
  im = Image.open('/home/pi/Directions_for_the_blind/segmentation_out.jpeg')
  width, height = im.size
  
  left_interval = im.crop((0, 0, width / 3, height))
  left_interval.save('left_interval.jpg')

  x1 = width / 3
  x2 = (width/3) * 2
  
  center_interval = im.crop((x1, 0, x2, height))
  center_interval.save('center_interval.jpg')

  x3 = width 
  right_interval = im.crop((x2, 0, x3, height))
  right_interval.save('right_interval.jpg')
  
def compute_interval_scores_RIGHT():
  im = Image.open('right_interval.jpg')

  sidewalk = 0
  road = 0
  stairway = 0

  for pixel in im.getdata():
      pixel = [pixel]

      sidewalk1 = [(64, 0, 128)]
      sidewalk2 = [(0, 0, 128)]
      fencing = [(128, 0, 64)]

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk1:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk2:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in fencing:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1


  confidence_val = (sidewalk // 1000)


  return confidence_val

def compute_interval_scores_LEFT():
  im = Image.open('left_interval.jpg')

  sidewalk = 0
  road = 0
  stairway = 0

  for pixel in im.getdata():
      pixel = [pixel]

      sidewalk1 = [(64, 0, 128)]
      sidewalk2 = [(0, 0, 128)]
      road_val = [(128, 128, 128)]
      stairway1 = [(64, 64, 192)]
      stairway2 = [(96, 192, 64)]
      fencing = [(128, 0, 64)]

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk1:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk2:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in fencing:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1


  confidence_val = (sidewalk // 1000)
  

  return confidence_val
        
def compute_interval_scores_CENTER():
  im = Image.open('center_interval.jpg')

  sidewalk = 0

  for pixel in im.getdata():
      pixel = [pixel]

      sidewalk1 = [(64, 0, 128)]
      sidewalk2 = [(0, 0, 128)]
      fencing = [(128, 0, 64)]

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk1:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in sidewalk2:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

      for r1, g1, b1 in pixel:
        for r2, g2, b2 in fencing:
            if abs(r1-r2) <= threshold:
              if abs(g1-g2) <= threshold:
                if (b1-b2) <= threshold:
                   sidewalk += 1

  confidence_val = (sidewalk // 1000)
 
  return confidence_val

def get_scores():
  segment_run()
  create_intervals()

  scores = [compute_interval_scores_LEFT(), compute_interval_scores_CENTER(),
            compute_interval_scores_RIGHT()]

  print('Scores: ', scores)
  max_value = max(scores)
  
  difference_from_straight_val = max_value - scores[1]

  if difference_from_straight_val >= 5:
    index = scores.index(max_value)
    route_recommendation = None

    if index == 0:
      route_recommendation = 'Slight left'

    elif index == 1:
      route_recommendation = 'Continue straight'

    elif index == 2:
      route_recommendation = 'Slight right'

  else:
    route_recommendation = 'Continue straight'

    
  return route_recommendation


#Latency ~ 5-6 seconds
