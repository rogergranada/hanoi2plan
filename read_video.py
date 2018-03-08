#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script binarize an image based on thresholds to HSV colors
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import cv2
import numpy as np


def extract_frames(path):
    """ Extract frames from video """
    cap = cv2.VideoCapture(path)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (800,600)) 

        # Display the resulting frame
        #cv2.imshow('frame',frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        break    

    return None




import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='file_input', help='Input video')
    args = parser.parse_args()

    extract_frames(args.inputfile)
