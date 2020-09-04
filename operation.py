import concurrent.futures
from functools import partial
import math
import time
import numpy as np
import matplotlib.mlab as mlab
from scipy.stats import norm
from itertools import  combinations
from scipy.spatial import distance
import sys
from matplotlib import pyplot as plt
import cv2
np.set_printoptions(threshold=sys.maxsize)

#class that applies OpenCV's blur followed by HoughCircles to return a list of circles with x,y coordinates
class hough_process():
    def hough(image, blur=5, dp=1, min_dist=80, canny_upper=86, hough_threshold=56, min_radius=0, max_radius=0):
        image2 = cv2.medianBlur(image,blur)
        circles = cv2.HoughCircles(image2,cv2.HOUGH_GRADIENT,dp,min_dist,
                                    param1=canny_upper,
                                     param2=hough_threshold,
                                     minRadius=min_radius,
                                     maxRadius=max_radius)



        return circles[0]

class tiles():
    def __init__(self, image, tile_size=800, overlap=0):
        self.image = image
        self.height, self.width = self.image.shape[:2]
        self.tile_size = tile_size
        self.overlap = overlap
        self.no_tiles_x = math.floor(self.width/(self.tile_size-self.overlap))
        self.no_tiles_y = math.floor(self.height/(self.tile_size-self.overlap))
        self.current_image = None

    def iotile(self, function, args, kwargs, location):
        #generates offsets
        x_offset = (self.tile_size*location[0])
        y_offset = (self.tile_size*location[1])
        img = self.image[int(y_offset):(int(y_offset)+self.tile_size%self.height),
                                            int(x_offset):(int(x_offset)+self.tile_size%self.width)]
        try:
            small_array = (function(img, *args, **kwargs))
            #print(small_array)
            small_array = np.uint16(np.around(small_array))
            small_array[:,0] = small_array[:,0]+x_offset
            small_array[:,1] = small_array[:,1]+y_offset
            return small_array

        except:
            return None

    def tile(self, function, *args, outputs=3, **kwargs):
        start = time.perf_counter()
        partial_iotile = partial(self.iotile, function, args, kwargs)
        locations = []
        large_array = np.empty((0,3), int)
        for i in range(0, self.no_tiles_x):
            for j in range(0, self.no_tiles_y):
                    locations.append((i,j))
        print(locations)
        print('Please Wait, Calclulating...')
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(partial_iotile, locations)
            for i in results:
                if isinstance(i, (np.ndarray, np.generic)) == True:
                    large_array = np.append(large_array, i, axis=0)
        finish = time.perf_counter()
        print('finished in', start-finish, 'seconds')
        return large_array

    def remove_doubles(self, input_array, separation=10):
            input_array = np.append(input_array,np.full((len(input_array),1), False), axis=1)
            distances_between = (distance.pdist(input_array[:,:2]))
            poss_comb = (list(combinations(range(len(input_array)),2)))


            for i in range(len(distances_between)):
                    if distances_between[i] < separation:
                        #print("the following are too close:")
                        #print(circles[poss_comb[i][0]],input_array[poss_comb[i][1]])
                        #if radius is bigger mark for removal
                        if input_array[poss_comb[i][0]][2] < input_array[poss_comb[i][1]][2]:
                            input_array[poss_comb[i][1]][3] = True
                        else:
                            input_array[poss_comb[i][1]][3] = True
            #print ('\n--marked array-- \n', input_array, '\n')
                #remove doubles
            input_array = input_array[input_array[:,3] == False]
            input_array = np.delete(input_array, 3, axis=1 )
            #print ('\n--Doubles removed-- \n', input_array, '\n')
            #print(distances_between)

            return input_array


#----------------------RUN CODE-------------------------------#
'''
#load image
input_img = cv2.imread('test-img.JPG',1)
eb_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
#creates an instance of the tile set
tile_array1 = tiles(eb_img)
#applies a given function across each of the the tiles and returns a list
circles = tile_array1.tile(hough_process.hough, blur=5, dp=1, min_dist=80, canny_upper=86, hough_threshold=56, min_radius=0, max_radius=0)
#function to remove close items (distance given) introduced by overlapping
circles = tile_array1.remove_doubles(circles, separation=100)








#*display output*
for i in circles:
    #draw the outer circle
    cv2.circle(input_img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv2.circle(input_img,(i[0],i[1]),2,(0,0,255),3)

plt.figure('Histogram')
plt.hist(circles[:,2], bins = 10)
plt.figure('Picture', figsize=[10,10])
input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
plt.imshow(input_img, cmap='gray')
plt.show()
'''
