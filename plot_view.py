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

class DrawGraph:
    def __init__(self, image='Houghscan Background.png', tile_size= 800):
        self.image = image
        self.img = mpimg.imread(self.image)
        self.tile_size= tile_size
        self.fig = Figure()
        self.fig2 = Figure()

        self.ax = self.fig.add_subplot(111)
        self.axzoom = self.fig2.add_subplot(111)
        self.fig2.tight_layout()
        self.fig.savefig('edit.jpg', quality=100)
        self.fig.tight_layout()
        self.x=550
        self.y=750
        self.drawzoom()
        self.draw()
        self.canvas = FigureCanvas(self.fig)
        self.zoomcanvas = FigureCanvas(self.fig2)
        self.zoomcanvas.set_size_request(self.tile_size/4, self.tile_size/4)

    def draw(self):
        self.ax.cla()
        self.ax.grid(False)
        self.ax.axis('off')
        self.ax.imshow(self.img)
        self.fig.canvas.draw()


    def drawzoom(self, params=None):
        self.axzoom.cla()
        self.zoomed_image = mpimg.imread(self.image)[int(self.y)-int(self.tile_size/2): int(self.y)+int(self.tile_size/2),
                                    int(self.x)-int(self.tile_size/2) : int(self.x)+int(self.tile_size/2)]

        eb_img = cv2.cvtColor(self.zoomed_image, cv2.COLOR_BGR2GRAY)
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
                self.axzoom.cla()
                self.axzoom.axis('off')
                self.axzoom.imshow(self.zoomed_image)

        except:
            self.axzoom.cla()
            self.axzoom.axis('off')
            self.axzoom.imshow(self.zoomed_image)
            pass


    def zoom(self, x, y, **kwargs):
        self.x = x
        self.y = y
        self.drawzoom(**kwargs)
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
