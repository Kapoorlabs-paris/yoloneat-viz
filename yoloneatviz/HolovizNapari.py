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
Boxname = 'ImageIDBox'
EventBoxname = 'EventIDBox'


class NEATViz(object):

        def __init__(self, imagedir, savedir, categories_json, fileextension = '*tif'):
            
            
               self.imagedir = imagedir
               self.savedir = savedir
               self.categories_json = categories_json
               self.fileextension = fileextension
               Path(self.savedir).mkdir(exist_ok=True)
               self.viewer = napari.Viewer()
               self.time = 0
               self.load_json()
               self.key_categories = self.load_json()
               
               
               
               self.showNapari()
               
        def load_json(self):
            with open(self.categories_json, 'r') as f:
                return json.load(f)        
        
        def showNapari(self):
                 
                 
                 Raw_path = os.path.join(self.imagedir, self.fileextension)
                 X = glob.glob(Raw_path)
                 Imageids = []
                 
                 for imagename in X:
                     Imageids.append(imagename)
                 
                 
                 eventidbox = QComboBox()
                 eventidbox.addItem(EventBoxname)
                 for (event_name,event_label) in self.key_categories.items():
                     
                     eventidbox.addItem(event_name)
                    
                 imageidbox = QComboBox()   
                 imageidbox.addItem(Boxname)   
                 detectionsavebutton = QPushButton(' Save Clicks')
                 
                 for i in range(0, len(Imageids)):
                     
                     
                     imageidbox.addItem(str(Imageids[i]))
                     
                     
                 self.figure = plt.figure(figsize=(4, 4))
                 self.multiplot_widget = FigureCanvas(self.figure)
                 self.ax = self.multiplot_widget.figure.subplots(1, 1)
                 width = 400
                 dock_widget = self.viewer.window.add_dock_widget(
                 self.multiplot_widget, name="EventStats", area='right')
                 self.multiplot_widget.figure.tight_layout()
                 self.viewer.window._qt_window.resizeDocks([dock_widget], [width], Qt.Horizontal)   
                 
                 
                 eventidbox.currentIndexChanged.connect(lambda eventid = eventidbox : self.csv_add(
                         
                         
                         os.path.basename(os.path.splitext(imageidbox.currentText())[0]),
                         eventidbox.currentText()
                    
                )
            )    
                 
                 imageidbox.currentIndexChanged.connect(
                 lambda trackid = imageidbox: self.image_add(
                         
                         imageidbox.currentText(),
                         
                         os.path.basename(os.path.splitext(imageidbox.currentText())[0])
                    
                )
            )            
                 
                    
                 
                 self.viewer.window.add_dock_widget(imageidbox, name="Image", area='left') 
                 self.viewer.window.add_dock_widget(eventidbox, name="Event", area='left')  
                 
                 
                        
        def csv_add(self, imagename, csv_event_name ):
            
            
            self.event_name = csv_event_name
            for (event_name,event_label) in self.key_categories.items():
                                
                                if event_label > 0 and csv_event_name == event_name:
                                     
                                     for layer in list(self.viewer.layers):
                                          
                                         if event_name in layer.name or layer.name in event_name or event_name + 'angle' in layer.name or layer.name in event_name + 'angle' :
                                                    self.viewer.layers.remove(layer)           
                                       
                                     
                                     self.csvname = self.savedir + "/" + event_name + "Location" + (os.path.splitext(os.path.basename(imagename))[0] + '.csv')
                                     
            self.dataset   = pd.read_csv(self.csvname, delimiter = ',')
            self.ax.cla()
            #Data is written as T, Y, X, Score, Size, Confidence
            self.T = self.dataset[self.dataset.keys()[0]][1:].astype('int16')
            self.Y = self.dataset[self.dataset.keys()[1]][1:]
            self.X = self.dataset[self.dataset.keys()[2]][1:]
            self.Score = self.dataset[self.dataset.keys()[3]][1:]
            self.Size = self.dataset[self.dataset.keys()[4]][1:]
            self.Confidence = self.dataset[self.dataset.keys()[5]][1:]
            
           
            timelist = []
            eventlist= []
            for i in range(1, self.image.shape[0]):
                
                condition = self.dataset["T"] == i
                countT = len(self.T[condition])
                timelist.append(i)
                eventlist.append(countT)
            
            self.ax.plot(timelist, eventlist, '-r')
            self.ax.set_title(self.event_name + "Events")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Counts")
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()
            plt.savefig(self.savedir  + self.event_name   + '.png')                         
            self.viewer.dims.events.current_step.connect(self.update_slider)
                                        
                                     
                                        
            
        def image_add(self, image_toread, imagename):
                                    
                for layer in list(self.viewer.layers):
                                         if 'Image' in layer.name or layer.name in 'Image':
                                                    self.viewer.layers.remove(layer)
                self.image = daskread(image_toread)
                if len(self.image.shape) > 3:
                    self.image = self.image[0,:]
                self.viewer.add_image(self.image, name= 'Image' + imagename )
                
                                                    
                
                                            
        def update_slider(self, event):
                  
                        self.time = int(self.viewer.dims.point[0])        
                        print('loop', self.time)    
                       
                        condition = self.dataset["T"] == self.time
                        limitT = self.T[condition]
                        limitX = self.X[condition]
                        limitY = self.Y[condition]
                        limitScore = self.Score[condition]
                        limitSize = self.Size[condition]
                        limitConfidence = self.Confidence[condition]
                        
                        listtime = limitT.tolist()
                        listy = limitY.tolist()
                        listx = limitX.tolist()
                        listsize = limitSize.tolist()
                        listscore = limitScore.tolist()
                        event_locations = []
                        size_locations = []
                        score_locations = []
                        for i in (range(len(listtime))):
                             tcenter = int(listtime[i])
                             ycenter = listy[i]
                             xcenter = listx[i]
                             size = listsize[i]
                             score = listscore[i]
                             event_locations.append([tcenter, ycenter, xcenter])   
                             size_locations.append(size)
                             score_locations.append(score)
                        for layer in list(self.viewer.layers):
                                          
                                         if self.event_name in layer.name or layer.name in self.event_name or self.event_name + 'angle' in layer.name or layer.name in self.event_name + 'angle' :
                                                    self.viewer.layers.remove(layer) 
                        self.viewer.add_points(event_locations, size = size_locations , name = self.event_name, face_color = [0]*4, edge_color = "red", edge_width = 1) 
