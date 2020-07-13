#!/usr/bin/python3
from operation import hough_process
from gi.repository import Gtk
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import numpy as np
from matplotlib import pyplot as plt
from numpy import random
import cv2

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
#sets ups graphs/diagrams of image to be analysed/it's preview
class DrawGraph:
    def __init__(self, image='Houghscan Background.png', tile_size= 800):
        #image is a pointer to the location of current background image
        self.image = image
        #imports the image using location 'self.image'
        #Note! this is changed by a setter in houghscan.py to an annotated version after processing
        self.img = mpimg.imread(self.image)
        self.tile_size= tile_size
        #instantiates two matplotlib figures for main diagram(fig) and preview(fig2)
        self.fig = Figure()
        self.fig2 = Figure()

        #creates an axis for main diagram - fig
        self.ax = self.fig.add_subplot(111)
        #creates axis for preview - fig 1
        self.axzoom = self.fig2.add_subplot(111)
        #matplotlib setting for smaller borders
        self.fig2.tight_layout()
        self.fig.tight_layout()
        #improved dpi setting for saving image (via matplotlib save button)
        self.fig.savefig('edit.jpg', quality=100)

        #default x and y location ###!
        self.x=550
        self.y=750

        #class methods to draw diagrams (zoom and main)
        self.drawzoom()
        self.draw()

        #sets up a canvas from figure to use in GTK (function from matplotlib.backends.backend_gtk3)
        self.canvas = FigureCanvas(self.fig)
        self.zoomcanvas = FigureCanvas(self.fig2)
        #scales tile size for preview
        self.zoomcanvas.set_size_request(self.tile_size/4, self.tile_size/4)

    def draw(self):
        #clears axis
        self.ax.cla()
        #matplotlib function to remove grid
        self.ax.grid(False)
        #matplotlib function to remove axis
        self.ax.axis('off')
        #sets axis to current annotated/unannotated import image
        self.ax.imshow(self.img)
        #matplotlib function to redraw canvas
        self.fig.canvas.draw()


    def drawzoom(self, params=None):
        #clears axis
        self.axzoom.cla()
        #displays a slice of the image a tile size around the location of the mouse location last clicked(x,y)
        #note - reimports for blank image
        self.zoomed_image = mpimg.imread(self.image)[int(self.y)-int(self.tile_size/2): int(self.y)+int(self.tile_size/2),
                                    int(self.x)-int(self.tile_size/2) : int(self.x)+int(self.tile_size/2)]
        #converts the image to greyscale for the Hough process
        eb_img = cv2.cvtColor(self.zoomed_image, cv2.COLOR_BGR2GRAY)
        #runs hough process from operation.py, returns an array where i[0] is x, i[1] is y and i[2] is radius
        try:
            hough_data = hough_process.hough(eb_img, blur=params.blur,
                                                    canny_upper=params.canny_detection,
                                                    min_dist=params.min_dist,
                                                    hough_threshold=params.hough_threshold,
                                                    min_radius=params.min_radius,
                                                    max_radius=params.max_radius)

            for i in hough_data:
                #draw the outer circle
                cv2.circle(self.zoomed_image,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(self.zoomed_image,(i[0],i[1]),2,(0,0,255),3)
                #clears axis
                self.axzoom.cla()
                #matplotlib funciton to hide axis
                self.axzoom.axis('off')
                #shows annotated image on preview axis
                self.axzoom.imshow(self.zoomed_image)

        #if no circles are detected (i.e incorrect paramters) display unannotated image
        except:
            self.axzoom.cla()
            self.axzoom.axis('off')
            self.axzoom.imshow(self.zoomed_image)
            pass

    def zoom(self, x, y, **kwargs):
        #sets mouse x and y locations from arguments
        self.x = x
        self.y = y
        #generates diagram using new x,y location
        self.drawzoom(**kwargs)
        #redraws canvas
        self.fig2.canvas.draw()

class DrawHistogram:
    def __init__(self):
        self.f = Figure(figsize=(5, 4), dpi=100)
        self.a = self.f.add_subplot(111)
        #self.t = np.arange(0.0, 3.0, 0.01)
        #self.s = np.sin(2*3.14*self.t)
        #self.a.plot(self.t, self.s)
        self.canvas = FigureCanvas(self.f)  # a Gtk.DrawingArea
        self.canvas.set_size_request(800, 600)

    def draw(self, data, bin_no=10):
        self.a.cla()
        self.a.hist(data[:,2], bins = bin_no)
        self.canvas.draw()
