#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:05:15 2021

@author: aimachine
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 14:50:47 2021

@author: vkapoor
"""
from tifffile import imread, imwrite
import csv
import napari
import glob
import os
import sys
import numpy as np
import json
from pathlib import Path
from scipy import spatial
import itertools
from napari.qt.threading import thread_worker
import matplotlib.pyplot  as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QPushButton, QSlider
import h5py
import cv2
import pandas as pd
import imageio
from dask.array.image import imread as daskread



class Zmapgen(object):

        def __init__(self, imagedir, savedir, append_name = "_Colored" , fileextension = '*tif', show_after = 1):
            
            
               self.imagedir = imagedir
               self.savedir = savedir
               self.fileextension = fileextension
               Path(self.savedir).mkdir(exist_ok=True)
               
               
        def genmap(self):
                 
                 
                 Raw_path = os.path.join(self.imagedir, self.fileextension)
                 X = glob.glob(Raw_path)
                 
                 count = 0
                 for fname in X:
                     
                     Name = os.path.basename(os.path.splitext(fname)[0])
                     if append_name in Name:
                        image = imread(fname)
                        count = count + 1
                        Signal_first = image[1,:]
                        Signal_second = image[2,:]
                     
                        Sum_signal_first = np.sum(Signal_first, axis = 0)
                        Sum_signal_second = np.sum(Singal_second, axis = 0)
                        
                        doubleplot(Sum_signal_first, Sum_signal_second, "First Channel Z map", "Second Channel Z map")
                        
                        imwrite(self.savedir + Name + 'Channel1' + '.tif', Sum_signal_first.astype('uint16'))
                        imwrite(self.savedir + Name + 'Channel2' + '.tif', Sum_signal_second.astype('uint16'))
                        
                        
                        
def doubleplot(imageA, imageB, titleA, titleB):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes.ravel()
    ax[0].imshow(imageA, cmap=cm.Spectral)
    ax[0].set_title(titleA)
    
    ax[1].imshow(imageB, cmap=cm.Spectral)
    ax[1].set_title(titleB)
    
    plt.tight_layout()
    plt.show()                         