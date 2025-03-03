import math
import time
import numpy as np
import cv2
from multiprocessing import Event
from multiprocessing import Pool
from functools import partial
import threading

np.set_printoptions(threshold=np.inf)

# Global event for cancellation
cancel_event = Event()
def init_worker():
    # This properly imports the global cancel_event into the worker process
    global cancel_event
    # No need to set any attributes

class CircleDetector:
    @staticmethod
    def detect_circles(image: np.ndarray, blur: int = 5, dp: int = 1, min_dist: int = 80,
                       canny_upper: int = 86, hough_threshold: int = 56,
                       min_radius: int = 0, max_radius: int = 0,
                       timeout: float = None) -> np.ndarray:
        """
        Applies OpenCV's blur followed by HoughCircles to return a list of circles with x, y coordinates.
        If timeout is set, the function will stop execution if it exceeds the given time.
        Instead of raising an error, it will return an empty array.
        """
        result = []
        exception = None

        def worker():
            nonlocal result, exception
            try:
                blurred_image = cv2.medianBlur(image, blur)
                circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp, min_dist,
                                           param1=canny_upper, param2=hough_threshold,
                                           minRadius=min_radius, maxRadius=max_radius)
                result = circles[0].astype(int) if circles is not None else np.empty((0, 3), int)
            except Exception as e:
                exception = e

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout)  # Wait for the thread to finish within the timeout period

        if thread.is_alive():
            # If still running after timeout, do not raise an error, just return empty array
            return np.empty((0, 3), int)

        return result if not exception else np.empty((0, 3), int)



    
def apply_function_and_position(function, args, kwargs, tile):
    """Standalone function to apply detection and adjust positions (picklable)."""
    x_offset, y_offset, img = tile

    if cancel_event.is_set():
        return np.empty((0, 3), int)  # Return empty array if canceled

    try:
        tile_result = function(img, *args, **kwargs)
        if isinstance(tile_result, np.ndarray) and tile_result.shape[0] > 0:
            tile_result[:, 0] += x_offset  # Adjust X coordinates
            tile_result[:, 1] += y_offset  # Adjust Y coordinates
            return tile_result
    except Exception as e:
        print(f"⚠️ Error processing tile at ({x_offset}, {y_offset}): {e}")

    return np.empty((0, 3), int)

class TileProcessor:
    def __init__(self, image: np.ndarray, tile_size: int = 800, overlap: int = 0):
        self.image = image
        self.height, self.width = self.image.shape[:2]
        self.tile_size = tile_size
        self.overlap = overlap
        self.no_tiles_x = math.ceil(self.width / (self.tile_size - self.overlap))
        self.no_tiles_y = math.ceil(self.height / (self.tile_size - self.overlap))
        self.executor = None  # Store ProcessPoolExecutor as an instance variable

    def split_into_tiles(self):
        """Split the image into picklable tuples for multiprocessing."""
        tiles = []
        for i in range(self.no_tiles_x):
            for j in range(self.no_tiles_y):
                x_start = i * (self.tile_size - self.overlap)
                y_start = j * (self.tile_size - self.overlap)
                img = self.image[
                    y_start:y_start + self.tile_size,
                    x_start:x_start + self.tile_size
                ]
                tiles.append((x_start, y_start, img))  # 🔹 Store as picklable tuple
        return tiles

    def remove_overlapping_circles(self, circles: np.ndarray, separation: int = 10) -> np.ndarray:
        """Remove overlapping circles resulting from tiling process."""
        if circles.size == 0:
            return circles  # Return empty array if no circles detected
        
        marked_for_removal = np.full(len(circles), False)

        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                if np.linalg.norm(circles[i, :2] - circles[j, :2]) < separation:
                    marked_for_removal[i] = True

        return circles[~marked_for_removal]


    def process_tiles_parallel(self, function: callable, *args, **kwargs) -> np.ndarray:
        """Processes image tiles in parallel and ensures cleanup after cancellation."""
        
        # Create a wrapped function with fixed parameters
        worker_func = partial(apply_function_and_position, function, args, kwargs)
        
        tiles = self.split_into_tiles()
        
        # Make sure cancel_event is reset before starting a new run
        cancel_event.clear()
        
        all_results = []
        
        try:
            # Use 'spawn' context explicitly for Windows compatibility
            with Pool(initializer=init_worker) as pool:
                # Process in smaller batches to allow for cancellation checking
                batch_size = max(1, len(tiles) // 10)  # Process ~10% at a time
                for i in range(0, len(tiles), batch_size):
                    batch = tiles[i:i+batch_size]
                    
                    # Start processing this batch
                    result_async = pool.map_async(worker_func, batch)
                    
                    # Wait for results with timeout to check cancellation
                    while not result_async.ready():
                        if cancel_event.is_set():
                            print("🔴 Processing canceled. Terminating workers...")
                            pool.terminate()
                            return np.empty((0, 3), int)
                        time.sleep(0.1)
                    
                    # Add batch results
                    batch_results = result_async.get()
                    all_results.extend(batch_results)
                    
                    # Check for cancellation between batches
                    if cancel_event.is_set():
                        print("🔴 Processing canceled between batches...")
                        return np.empty((0, 3), int)
        
        except Exception as e:
            print(f"⚠️ Error in processing: {e}")
            return np.empty((0, 3), int)
        
        # Filter out empty results and concatenate
        valid_results = [r for r in all_results if r.size > 0]
        all_circles = np.concatenate(valid_results, axis=0) if valid_results else np.empty((0, 3), int)
        return self.remove_overlapping_circles(all_circles, separation=100)

