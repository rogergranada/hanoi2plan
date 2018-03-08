#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import linecache
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import ast
import numpy as np
from os.path import realpath, dirname, splitext
from os.path import basename, isfile, isdir, join

from classes import progressbar

def is_file(inputfile):
    """ Check whether the ``inputfile`` corresponds to a file """
    inputfile = realpath(inputfile)
    if not isfile(inputfile):
        logger.error('Input is not a file!')
        sys.exit(0)
    return inputfile


def is_folder(inputfolder):
    """ Check whether the ``inputfolder`` corresponds to a folder """
    inputfolder = realpath(inputfolder)
    if not isdir(inputfolder):
        logger.error('Argument %s is not a folder!' % inputfolder)
        sys.exit(0)
    return inputfolder


def add_text2path(path, text, withfolder=True):
    """ Add text to the end of the pathfile -- before the extension """
    path = realpath(path)
    dirfile = dirname(path)
    fname, ext = splitext(basename(path))
    fileout = fname+"_"+str(text)+ext
    if withfolder:
        return join(dirfile, fileout)
    return fileout


def filename(path, extension=True):
    fname, ext = splitext(basename(path))
    if extension:
        return fname, ext
    return fname


def add2dic(dic, key, value):
    if dic.has_key(key):
        dic[key].append(value)
    else:
        dic[key] = [value]
    return dic


class PathfileHandler(object):
    """Class to deal with files containing paths and labels/features"""

    def __init__(self, inputfile, display=True):
        """Initializes the class
        
        Parameters
        ----------
        inputfile : string
            path to the file containing images and labels/features
        display : boolean
            show the progress bar
        """
        self.display = display
        self.inputfile = realpath(inputfile)
        self.inputdir = dirname(inputfile)
        self.nb_lines = self.count_lines(inputfile)
        self.path = None
        self.label = None
        self.feats = None
        logger.debug('Loading file: %s' % inputfile)


    def __iter__(self):
        """Iterates the file yielding the path, the true label and a vector of 
        features when exists
        """
        pb = progressbar.ProgressBar(self.nb_lines)
        with open(self.inputfile) as fin:
            for line in fin:
                arr = line.strip().split()
                if len(arr) == 1:
                    self.path = arr
                    yield self.path
                elif len(arr) > 1:
                    self.path = arr[0]
                    self.label = arr[1]
                    if len(arr) > 2:
                        if len(arr[2:]) == 1:
                            self.feats = ast.literal_eval(arr[2])
                        else:
                            self.feats = map(float, arr[2:])
                        yield self.path, self.label, self.feats
                    else:
                        yield self.path, self.label
                if self.display:
                    pb.update()


    @staticmethod
    def count_lines(inputfile):
        """ Returns the total number of images in the input file 

        Parameters
        ----------
        inputfile : string
            path to the file containing images and labels/features

        Returns
        -------
        n : int
            total number of lines in the document
        """
        with open(inputfile) as fin:
            for n, _ in enumerate(fin, start=1): pass
        return n


    def get_line(self, nb_line):
        """Returns the line at number `nb_line`"""
        return linecache.getline(self.inputfile, nb_line).strip()


    def get_path(self, nb_line, label=False):
        """Returns the path of the line at number `nb_line`"""
        line = linecache.getline(self.inputfile, nb_line)
        path = None
        if line:
            arr = line.split()
            path = arr[0]
            if label:
                y = arr[1]
                return path, y
        return path


    def get_label(self, nb_line):
        """Returns the path of the line at number `nb_line`"""
        line = linecache.getline(self.inputfile, nb_line)
        label = None
        if line:
            label = line.split()[1]
        return label


    def features_line(self, nb_line, asstr=False):
        """Returns only the feature of the line number `nb_line`"""
        line = linecache.getline(self.inputfile, nb_line)
        arr = line.strip().split()
        if len(arr) > 2:
            if asstr:
                return ' '.join(arr[2:])
            else:
                return arr[2:]
        return None


    def current_features(self, N=2):
        """
        Return a list containing the `N` features with the highest scores

        Parameters:
        -----------
        N : int
            number of features to return

        Notes:
        ------
        The output has the form of a list as:
        [(1, 0.33), (3, 0.12), (5, 0.08), ...]
        """
        features = self.labels[1:]
        classes = map(int, features[0::2])
        preds = np.array(features[1::2], dtype=np.float32)
        topN = []
        for n in range(N):
            valmax = preds.max()
            imax = preds.argmax()
            topN.append((classes[imax], valmax))
            preds[imax] = -1
        return topN


    def has_features(self):
        """
        Returns
        -------
        _ : bool
            False : only path and label
            True : path, label and features
        """
        line = self.get_line(1)
        arr = line.strip().split()
        if len(arr) > 2:
            return True
        else:
            return False
#End of class PathfileHandler


class Videos(PathfileHandler):
    """ Class to extract videos from files """

    def __init__(self, inputfile, dataset_name):
        PathfileHandler.__init__(self, inputfile, display=False)

        self.videos = {}
        self.name = None
        self.is_dataset(dataset_name)


    def is_dataset(self, dtname):
        nm_data = dtname.lower()
        if nm_data in ("dogcentric", "dogs"):
            self.name = "dogs"
        elif nm_data in ("kscgr", "kitchen"):
            self.name = "kscgr"
        elif nm_data in ("ucf11", "ucf-11"):
            self.name = "ucf11"
        else:
            logger.error("Dataset %s does not exists!" % nm_data)
            sys.exit(0)


    def _videos_dogs(self, nb_frames=False):
        # ~/Car/Car_Ringo_5_9810_9910_frame_83.jpg
        fname, ext = splitext(basename(self.path))
        nm_video, frame = fname.split('_frame_')
        if nb_frames:
            frame = int(frame)
            add2dic(self.videos, nm_video, frame)
        else:
            add2dic(self.videos, nm_video, (self.path, self.label))


    def _videos_kscgr(self, nb_frames=False):
        # ~/Data/data1/boild-egg/img256/0.jpg
        arr = self.path.split('/')
        nm_video = arr[-4]+'_'+arr[-3]+'_'+arr[-2]
        if nb_frames:
            frame, ext = splitext(basename(self.path))
            frame = int(frame)
            add2dic(self.videos, nm_video, frame)
        else:
            add2dic(self.videos, nm_video, (self.path, self.label))


    def _videos_ucf11(self, nb_frames=False):
        # ~/basketball/v_shooting_14/v_shooting_14_01/image_00001.jpg
        arr = self.path.split('/')
        nm_video = arr[-4]+'_'+arr[-3]+'_'+arr[-2]
        if nb_frames:
            frame, ext = splitext(basename(self.path))
            frame = int(frame.split('_')[1])
            add2dic(self.videos, nm_video, frame)
        else:
            add2dic(self.videos, nm_video, (self.path, self.label))


    def extract_videos(self):
        """ create a dictionary containing {video_name: [frames]} """
        for k in self:
            if self.name == "dogs":
                self._videos_dogs()
            elif self.name == "kscgr":
                self._videos_kscgr()
            elif self.name == "ucf11":
                self._videos_ucf11()
        return self.videos
#End of class Videos


class Images(PathfileHandler):
    """ Class to extract videos from files """

    def __init__(self, inputfile, dataset_name):
        PathfileHandler.__init__(self, inputfile, display=False)

        self.name = None
        self.root = None
        self.fname = None
        self.is_dataset(dataset_name)


    def is_dataset(self, dtname):
        nm_data = dtname.lower()
        if nm_data in ("dogcentric", "dogs"):
            self.name = "dogs"
        elif nm_data in ("kscgr", "kitchen"):
            self.name = "kscgr"
        elif nm_data in ("ucf11", "ucf-11"):
            self.name = "ucf11"
        else:
            logger.error("Dataset %s does not exists!" % nm_data)
            sys.exit(0)


    def _paths_dogs(self):
        # ~/Car/Car_Ringo_5_9810_9910_frame_83.jpg
        arr = self.path.split('/')
        self.root = '/'.join(arr[0:-2])
        self.fname = '/'.join(arr[-2:])


    def _paths_kscgr_ucf11(self):
        # ~/data1/boild-egg/img256/0.jpg
        # ~/basketball/v_shooting_14/v_shooting_14_01/image_00001.jpg
        arr = self.path.split('/')
        self.root = '/'.join(arr[0:-4])
        self.fname = '/'.join(arr[-4:])


    def extract_root(self):
        """ extract the root and file name of paths """
        if self.name == "dogs":
            self._paths_dogs()
        elif self.name in ("kscgr", "ucf11"):
            self._paths_kscgr_ucf11()
        return self.root, self.fname
#End of class Videos
