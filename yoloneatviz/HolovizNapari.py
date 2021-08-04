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
                     
                     
                 figure = plt.figure(figsize=(4, 4))
                 multiplot_widget = FigureCanvas(figure)
                 ax = multiplot_widget.figure.subplots(1, 1)
                 width = 400
                 dock_widget = self.viewer.window.add_dock_widget(
                 multiplot_widget, name="EventStats", area='right')
                 multiplot_widget.figure.tight_layout()
                 self.viewer.window._qt_window.resizeDocks([dock_widget], [width], Qt.Horizontal)    
                 eventidbox.currentIndexChanged.connect(lambda eventid = eventidbox : EventViewer(
                         self.viewer,
                         eventidbox.currentText(),
                         self.key_categories,
                         os.path.basename(os.path.splitext(imageidbox.currentText())[0]),
                         self.savedir,
                         multiplot_widget,
                         ax,
                         figure
                    
                )
            )    
                 
                 imageidbox.currentIndexChanged.connect(
                 lambda trackid = imageidbox: EventViewer(
                         self.viewer,
                         imageidbox.currentText(),
                         self.key_categories,
                         os.path.basename(os.path.splitext(imageidbox.currentText())[0]),
                         self.savedir,
                         multiplot_widget,
                         ax,
                         figure
                    
                )
            )            
                 
                 self.viewer.window.add_dock_widget(imageidbox, name="Image", area='left') 
                 self.viewer.window.add_dock_widget(eventidbox, name="Event", area='left')  
                 
                 
                                     
      
                             
                             
          



                        
class EventViewer(object):
    
    def __init__(self, viewer, image_toread, key_categories, imagename, savedir, canvas, ax, figure):
        
           
           self.viewer = viewer
           self.image_toread = image_toread
           self.key_categories = key_categories
           self.imagename = imagename
           self.savedir = savedir
           self.canvas = canvas
           self.ax = ax
           self.figure = figure
           self.time = int(self.viewer.dims.point[0])
           image = daskread(self.image_toread)
           self.viewer.add_image(image, name= 'Image' + self.imagename )
           
           self.viewer.dims.events.current_step.connect(self.image_add)
    def image_add(self, event):
                            
        print('in')
        self.time = int(self.viewer.dims.point[0])
        
        print(self.time)
        
        for layer in list(self.viewer.layers):
                                 if 'Image' in layer.name or layer.name in 'Image':
                                            self.viewer.layers.remove(layer)
                                            
                                            
        
                                    
        for (event_name,event_label) in self.key_categories.items():
                        
                        if event_label > 0 and self.event_name == event_name:
        
                             for layer in list(self.viewer.layers):
                                  
                                 if event_name in layer.name or layer.name in event_name or event_name + 'angle' in layer.name or layer.name in event_name + 'angle' :
                                            self.viewer.layers.remove(layer)           
                               
                             
                             csvname = self.savedir + "/" + event_name + "Location" + (os.path.splitext(os.path.basename(self.imagename))[0] + '.csv')    
                             #event_locations, size_locations, timelist, eventlist = self.event_counter(csvname)
                             
                             #self.viewer.add_points(np.asarray(event_locations), size = size_locations ,name = event_name, face_color = [0]*4, edge_color = "red", edge_width = 1)
                             
                             
                             
                                      
                             
                             #self.viewer.theme = 'light'
                             #self.ax.plot(timelist, eventlist, '-r')
                             #self.ax.set_title(event_name + "Events")
                             #self.ax.set_xlabel("Time")
                             #self.ax.set_ylabel("Counts")
                             #self.figure.canvas.draw()
                             #self.figure.canvas.flush_events()
                             #plt.savefig(self.savedir  + event_name   + '.png')

                             
    def event_counter(self, csv_file):
     
         data   = pd.read_csv(csv_file, delimiter = ',')
         print(data(data["T"] == self.time))
         time = data["T"]
         y = data["Y"]
         x = data["X"]
         score = data["Score"]
         size = data["Size"]
         confidence = data["Confidence"] 
         
         
         
         
         eventcounter = 0
         eventlist = []
         timelist = []   
         listtime = time.tolist()
         listy = y.tolist()
         listx = x.tolist()
         listsize = size.tolist()
         listscore = score.tolist()
         event_locations = []
         size_locations = []
         for i in (range(len(listtime))):
             tcenter = int(listtime[i])
             ycenter = listy[i]
             xcenter = listx[i]
             size = listsize[i]
             print(tcenter)
             eventcounter = listtime.count(tcenter)
             timelist.append(tcenter)
             eventlist.append(eventcounter)
             event_locations.append([tcenter, ycenter, xcenter])   
             size_locations.append(size)
             
             
            
         return event_locations, size_locations, timelist, eventlist                    
