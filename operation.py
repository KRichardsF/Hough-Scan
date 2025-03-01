import concurrent.futures
import math
import time
from typing import List, Tuple, Union
import numpy as np
from itertools import combinations
import cv2

np.set_printoptions(threshold=np.inf)

class CircleDetector:
    @staticmethod
    def detect_circles(image: np.ndarray, blur: int = 5, dp: int = 1, min_dist: int = 80,
                       canny_upper: int = 86, hough_threshold: int = 56,
                       min_radius: int = 0, max_radius: int = 0) -> np.ndarray:
        """applies OpenCV's blur followed by HoughCircles to return a list of circles with x,y coordinates"""
        blurred_image = cv2.medianBlur(image, blur)
        circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp, min_dist,
                                   param1=canny_upper, param2=hough_threshold,
                                   minRadius=min_radius, maxRadius=max_radius)
        return circles[0].astype(int) if circles is not None else np.empty((0, 3), int)

class TileProcessor:
    def __init__(self, image: np.ndarray, tile_size: int = 800, overlap: int = 0):
        """TileProcessor object containing given parameters for tiling and functions to tile and process an image"""
        self.image = image
        self.height, self.width = self.image.shape[:2]
        self.tile_size = tile_size
        self.overlap = overlap
        self.no_tiles_x = math.ceil(self.width / (self.tile_size - self.overlap))
        self.no_tiles_y = math.ceil(self.height / (self.tile_size - self.overlap))

    class Tile():
        def __init__(self, x: int, y:int, img: np.ndarray):
            self.x = x
            self.y = y
            self.img = img

    def split_into_tiles(self):
        """Split the image into tiles (TileProcessor.Tile objects)."""
        tiles = []
        for i in range(self.no_tiles_x):
            for j in range(self.no_tiles_y):
                x_start = i * (self.tile_size - self.overlap)
                y_start = j * (self.tile_size - self.overlap)
                img = self.image[y_start:y_start + self.tile_size,
                                x_start:x_start + self.tile_size]
                tiles.append(self.Tile(i, j, img))
        return tiles

    def apply_function_and_position(self, function: callable, args: Tuple, kwargs: dict, tile: Tile) -> np.ndarray:
        """Apply a function to a tile and return result (circles) ajusted for any positioning needed wrt the larger image"""
        x_offset, y_offset, img = [tile.x, tile.y, tile.img]
        try:    
            tile_result = function(img, *args, **kwargs)
            if isinstance(tile_result, (np.ndarray, np.generic)):
                tile_result = self.position_circles(tile_result, x_offset, y_offset)
                return tile_result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def position_circles(self, tile_result: np.ndarray, x_offset: int, y_offset:int):
        """Offsets circle location according to tile position"""
        tile_result = np.uint16(np.around(tile_result))
        tile_result[:, 0] += x_offset * (self.tile_size - self.overlap)
        tile_result[:, 1] += y_offset * (self.tile_size - self.overlap)
        return tile_result

    def euclidean_distance(self, a, b):
        return np.linalg.norm(a - b)

    def remove_overlapping_circles(self, circles: np.ndarray, separation: int = 10) -> np.ndarray:
        """Remove overlapping circles resulting from tiling process (according to separation)."""
        marked_for_removal = np.full(len(circles), False)
        
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                if self.euclidean_distance(circles[i, :2], circles[j, :2]) < separation:
                    marked_for_removal[i] = marked_for_removal[j] = True

        valid_indices = np.where(~marked_for_removal)[0]
        return circles[valid_indices]
    
    def process_tiles_parallel(self, function: callable, *args, **kwargs) -> np.ndarray:
        """Tiles image and processes tiles in parallel using the specified function. Filters to correct for tiling and returns array of circles."""
        start_time = time.perf_counter()
        tiles = self.split_into_tiles()

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(executor.map(self.apply_function_and_position, [function] * len(tiles), [args] * len(tiles), [kwargs] * len(tiles), tiles))
        all_circles = np.concatenate(results, axis=0)
        filtered_circles = self.remove_overlapping_circles(all_circles, separation=100)

        finish_time = time.perf_counter()
        print(f'Processing finished in {finish_time - start_time:.2f} seconds')
        return filtered_circles


def main():
    input_img = cv2.imread('test-img.JPG', 1)
    gray_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)

    tile_processor = TileProcessor(gray_img)
    detected_circles = tile_processor.process_tiles_parallel(
        CircleDetector.detect_circles,
        blur=5, dp=1, min_dist=80, canny_upper=86, hough_threshold=56, min_radius=0, max_radius=0
    )

    for circle in detected_circles:
        cv2.circle(input_img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        cv2.circle(input_img, (circle[0], circle[1]), 2, (0, 0, 255), 3)

    plt.figure('Histogram')
    plt.hist(detected_circles[:, 2], bins=10)
    plt.figure('Picture', figsize=[10, 10])
    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
    plt.imshow(input_img, cmap='gray')
    plt.show()

if __name__ == "__main__":
    main()
