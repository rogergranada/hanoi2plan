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

def save_image(path, img):
    cv2.imwrite(path, img)


def extract_mask(image, lower, upper, erode=False, dilate=False):
    """ Apply mask on the image with lower and upper thresholds """
    kernel = np.ones((2,2),np.uint8)
    mask = cv2.inRange(image, lower, upper)
    if erode:
        e_mask = cv2.erode(mask, kernel, iterations=1)
        if dilate:
            d_mask = cv2.dilate(e_mask, kernel, iterations=1)
            return d_mask
        return e_mask
    if dilate:
        d_mask = cv2.dilate(mask, kernel, iterations=1)
        return d_mask
    return mask


def generate_contours(image, kernel_size=9):
    """ Generate only the contours to images """
    kernel = np.ones((kernel_size, kernel_size),np.uint8)
    img_dilated = cv2.dilate(image, kernel)
    img_contours = img_dilated - image
    return img_contours


def old_mask(image, fixed_size=(800,600), erode=False, dilate=False):
    image = cv2.imread(image)
    if fixed_size:
        image = cv2.resize(image, fixed_size) 
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #Stick and yellow disk
    yellow_lower = np.array([ 10,   90,    60])
    yellow_upper = np.array([ 40,  255,  255])
    yellow_mask = extract_mask(hsv, yellow_lower, yellow_upper, erode=erode, dilate=dilate)
    
    #Red disk
    red_lower = np.array([ 0,   60,    30])
    red_upper = np.array([ 10,  255,  255])
    red_mask = extract_mask(hsv, red_lower, red_upper, erode=erode, dilate=dilate)

    #Green disk
    green_lower = np.array([40,  60,   30])
    green_upper = np.array([55, 255,  255])
    green_mask = extract_mask(hsv, green_lower, green_upper, erode=erode, dilate=dilate)
    
    mask = yellow_mask + red_mask + green_mask
    
    """ experiments """
    #crop_img = mask[130:280, :]

    #crop_img = cv2.resize(crop_img, (65,15)) 
    return mask

def apply_on_gray(image, fixed_size=(800,600), erode=False, dilate=False):
    image = cv2.imread(image, 0)
    if fixed_size:
        image = cv2.resize(image, fixed_size) 

    white_lower = np.array([ 0])
    white_upper = np.array([ 115])
    mask = extract_mask(image, white_lower, white_upper, erode=erode, dilate=dilate)
    return mask


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def apply_mask(image, fixed_size=(800,600), erode=False, dilate=False):
    image = cv2.imread(image)
    image = rotate_image(image, 359)
    if fixed_size:
        image = cv2.resize(image, fixed_size) 
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #Stick and yellow disk
    yellow_lower = np.array([ 15,  70,  10])
    yellow_upper = np.array([ 30,  255,  255])
    yellow_mask = extract_mask(hsv, yellow_lower, yellow_upper, erode=erode, dilate=dilate)
    
    #Green disk
    green_lower = np.array([ 40,   60,   10])
    green_upper = np.array([ 70,  255,  255])
    green_mask = extract_mask(hsv, green_lower, green_upper, erode=erode, dilate=dilate)

    #Blue disk
    blue_lower = np.array([90,  60,   10])
    blue_upper = np.array([120, 255,  255])
    blue_mask = extract_mask(hsv, blue_lower, blue_upper, erode=erode, dilate=dilate)

    #Orange disk (bad but ok)
    orange_lower = np.array([5,  60,   10])
    orange_upper = np.array([15, 255,  255])
    orange_mask = extract_mask(hsv, orange_lower, orange_upper, erode=erode, dilate=dilate)
    
    mask = yellow_mask + green_mask + blue_mask + orange_mask
    #white_lower = np.array([ 0])
    #white_upper = np.array([ 115])
    #mask = extract_mask(image, white_lower, white_upper, erode=erode, dilate=dilate)
    #res = cv2.inRange(hsv, white_lower, white_upper)
    #mask = cv2.bitwise_and(image, image, mask= res)
    """ experiments """
    crop_img = mask[125:275, :]

    #crop_img = cv2.resize(crop_img, (80,15)) 
    #save_image('/home/roger/Desktop/small.jpg', crop_img)
    return crop_img


import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='file_input', help='Image file')
    args = parser.parse_args()

    mask = apply_mask(args.inputfile, fixed_size=(800,600), erode=False, dilate=False)
    cv2.imshow("window", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
