#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
from os.path import join, splitext, basename, dirname
from os.path import realpath, abspath, exists, isdir

import argparse
import ast
from Tkinter import Tk, Label, Listbox, END, N, S, W
from PIL import Image, ImageTk

import transform_image

def is_folder(inputfolder):
    """ Check whether the ``inputfolder`` corresponds to a folder """
    inputfolder = realpath(inputfolder)
    if not isdir(inputfolder):
        print('Argument %s is not a folder!' % inputfolder)
        sys.exit(0)
    return inputfolder

class ImageManager(object):
    """
    Class to manage the frames
    """
    def __init__(self, input):
        """
        Initiates the class ImageManager
    
        Parameters:
        -----------
        input : string
            path to the input file containing the paths to the images
            as well as the true values and the predicted values
        """
        self.input = realpath(input)
        self.imgdata = []
        self.index = 0
        self.width = 0
        self.height = 0
        self._loadImages()


    def __iter__(self):
        """
        Iterates over the images yielding the path of the image,
        the name of the image, the true label and the predicted label.
        """
        for path, name in self.imgdata:
            yield path, name

    
    def _check_size(self, pathimg):
        """Check the size of an image"""
        im = Image.open(pathimg)
        self.width, self.height = im.size


    def _loadImages(self):
        """
        Extract the content from the file and stores into an array.
        """
        self.imgdata = []
        with open(self.input) as fin:
            for line in fin:
                path = line.strip()
                name, ext = splitext(basename(path))
                self.imgdata.append((path, name))
                self._check_size(path)
        return self.imgdata


    def nextImage(self):
        """
        Return the path, true label and predicted label of the next image 
        in the list of images.
        """
        data = self.imgdata[self.index]
        if self.index < len(self.imgdata)-1:
            self.index += 1
        return data
#End of class ImageManager


class DemoWindow(Tk):
    """
    Class to manage the window of the demo
    """
    def __init__(self, fileinput, fixed_size=(800,600), erode=False, dilate=False, save=True, dirout=None):
        """
        Build the visual interface with images and fields to the images data
        """
        fileinput = realpath(fileinput)
        self.imgs = ImageManager(fileinput)
        if fixed_size:
            self.imgs.width = fixed_size[0]
            self.imgs.height = fixed_size[1]
        self.size = (self.imgs.width, self.imgs.height)

        self.erode = erode
        self.dilate = dilate
        self.save = save
        self.dirout = dirout

        Tk.__init__(self)
        self.title("Sequence of frames")
        # width x height + x_offset + y_offset:
        self.geometry(str(self.imgs.width+20)+"x"+str(self.imgs.height+30)+"+1+1")
        self.i = 0
        self.prev = 0

        #self.filelist = self.imgs._loadImages()
        self.filelist = self.imgs.imgdata

        self.frame = Label(self, text="")
        self.frame.grid(row=0, column=1, padx=10, pady=2, sticky=N+S+W)

        self.image = Label(self, image=None)
        self.image.grid(row=1, column=1, padx=10, pady=2, sticky=N+S+W)

        self.update_window()


    def updateImage(self, pathimg, binarize=True):
        """
        Updata the Label containing the image
        """
        if binarize:
            cv2_im = transform_image.apply_mask(pathimg, fixed_size=self.size, 
                                                erode=self.erode, dilate=self.dilate)
            #cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(cv2_im)
        else:
            im = Image.open(pathimg)
        self.tkimage = ImageTk.PhotoImage(im)
        self.image.configure(image=self.tkimage)
        if self.save:
            self.save_image(self.dirout, pathimg, cv2_im)


    def updateLabelFrame(self, text):
        """
        Update the label containing the number of the frame
        """
        self.frame.configure(text='Frame: '+text)


    def update_window(self):
        """
        Update the window and its elements every second
        """
        path, name = self.imgs.nextImage()
        self.updateImage(path)
        self.updateLabelFrame(name)
        self.after(1, self.update_window)


    def save_image(self, dirout, path, img):
        """ Save image in ``dirout`` folder """
        pathout = join(dirout, basename(path))
        transform_image.save_image(pathout, img)
#End of class DemoWindow


def create_file_paths(inputfolder, fileoutput):
    fout = open(fileoutput, 'w')

    path = realpath(inputfolder)
    files = os.listdir(inputfolder)
    names = []
    for img in files:
        name, ext = splitext(img)
        if ext in ('.jpg', '.JPG'):
            names.append(name)
    for name in sorted(names):
        fout.write('%s%s%s\n' % (inputfolder, name, ext))
    print 'Saved paths in file: %s' % fileoutput


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    """ Create file containing all paths ""
    parser.add_argument('inputfolder', metavar='folder_input', 
                        help='folder containing images.')
    parser.add_argument('outputfile', metavar='file_output', 
                        help='file to save paths of images.')
    args = parser.parse_args()
    create_file_paths(args.inputfolder, args.outputfile)
    """
    parser.add_argument('inputfile', metavar='file_input', 
                        help='file containing the paths of images.')
    parser.add_argument('-s', '--size', help='Size of the image. Added as: 800x600', default='None', type=str)
    parser.add_argument('-e', '--erode', help='Erode image mask', action='store_true')
    parser.add_argument('-d', '--dilate', help='Dilate image mask', action='store_true')
    parser.add_argument('-o', '--output', help='Path to the folder to save images', default='None', type=str)
    args = parser.parse_args()

    if args.size == 'None':
        size = None
    else:
        w, h = args.size.split('x')
        size = (int(w), int(h))

    save = False
    dirout = None
    if args.output != 'None':
        save = True
        dirout = is_folder(args.output)
    
    window = DemoWindow(args.inputfile, fixed_size=size, erode=args.erode, dilate=args.dilate, save=save, dirout=dirout)
    window.mainloop()
    
