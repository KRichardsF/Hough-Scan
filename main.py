try:
    import pyi_splash
    HAS_PYI_SPLASH = True
except ImportError:
    HAS_PYI_SPLASH = False

from fasthtml.common import *
from fasthtml.svg import SvgInb, Circle
from fasthtml.components import Defs, ClipPath, Rect, Image, G
from operation import CircleDetector, TileProcessor, cancel_event

from PIL import Image as PILImage
from components import button, menu, split, entry, selector

from pathlib import Path
import copy
import socket
import json
import time
import io
import base64
import csv
import sys
from multiprocessing import freeze_support
import threading
import requests
import webview
import os
import numpy as np
from dataclasses import dataclass
from typing import Optional
import signal
import platform
import sys
import uvicorn
from contextlib import asynccontextmanager
import importlib
from fastapi.responses import Response, FileResponse
from fastapi import BackgroundTasks

server = None

processing_active = False
# Store a reference to the tile processor so we can cancel it
tile_processor_instance = None

def find_available_port(starting_port=5001, max_attempts=10):
    """Finds an available port starting from `starting_port`."""
    for port in range(starting_port, starting_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:  # Port is free
                return port
    raise RuntimeError("No available ports found in the given range.")

# Find an available port at runtime
PORT = find_available_port()

def ft_path(*c, target_id=None, **kwargs):
    return ft_hx('path', *c, target_id=target_id, **kwargs)

def scan_name_generator():
    count = 1
    while True:
        yield f"Scan-{count}"
        count += 1

def get_base64_image(image, format="JPEG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"

@dataclass
class Parameters:
    scan_name: str = None
    scan_color: str = '#33D17A'
    blur: int = 5
    minimum_distance: int = 80
    canny_upper_limit: int = 80
    hough_threshold: int = 60
    minimum_radius: int = 0
    maximum_radius: int = 0
    tile_size: int = 500
    tile_overlap: int = 10
    doubles_removal_distance: int = 10
    detected_circles = []

@dataclass
class Settings:
    scan_name_gen = scan_name_generator()
    image_path: str = Path.cwd() / 'static' / 'images' / 'Houghscan Background.png'
    image = PILImage.open(image_path).convert("RGB")
    active_parameters = Parameters(scan_name=next(scan_name_gen))
    scan_parameters = [active_parameters]
    preview_position: tuple = (0,0)
    preview_scale: float = 0.5
    preview_size: int = 0

current_settings = Settings()

# Open the image once

headers = (
    Script(src="static/js/htmx.js", defer=True),
    Script(src="static/js/tailwind.js"),
    Script(src="static/js/alpine.js", defer=True),
    Script(src="/static/js/d3.js", defer=True),
    Script(src="/static/js/split.js", defer=True),
    Script(src="/static/js/fluid_spinbox.js"),
    Script(src="/static/js/d3_image_canvas.js", defer=True),
    # Link(rel="icon", type="image/x-icon", href="/images/favicon.ico"),
    Link(rel="stylesheet", type="text/css", href="/static/css/responsive.css"), 

)

app = FastHTML(hdrs=headers)

@app.get("/")
def home():
    return (
        Title("Hough Scan"),
        Div(
            # Main menu with updated endpoints:
            menu.top_menu(
                menu.menu_item(
                    'File',
                    menu.menu_selection('New',  keys=['Ctrl','n'], hx_swap='outerHTML', hx_post='/new', hx_target='body'),
                    # menu.menu_selection('Save as',  keys=['Alt','D'], hx_swap='none', hx_post='/save_as'),
                    # menu.menu_selection('Open', keys='o', hx_swap='none', hx_post='/open'),
                ),
                menu.menu_item(
                    'Export',
                    menu.menu_selection('Export CSV',  keys=['Ctrl','j'], hx_swap='none', hx_post='/export_csv'),
                    menu.menu_selection('Export JSON',  keys=['Ctrl','e'], hx_swap='none', hx_post='/export_json'),
                ),
            ),
            # Page Content
            Div(
                split.split_pane(["split-0", "split-1"], gutter_size=4, max_size=None, min_size=0, gutter_colour='#7040c8', sizes=[90,10]),
                Div(
                    # Main Canvas
                    Div(
                        Div(
                            Svg(
                                G(
                                    Image(
                                        href=get_base64_image(current_settings.image),
                                        id="loaded-image",
                                    ),
                                    G(
                                        id="circle-overlay-main",
                                    ),
                                    id="main-canvas"
                                ),
                                id="user-image",
                                style="width: 100%; height: 100%;"
                            ),
                            id="image-container",
                            cls="flex grow justify-center items-center h-full"
                        ),
                        cls="flex grow items-center justify-center w-7/8 border-r border-gray-100 bg-gray-50"
                    ),
                    # Tile Bar
                    Div(
                        entry.number_input(
                            'Tile Size',
                            current_value=current_settings.active_parameters.tile_size,
                            maximum_value=6000,
                            minimum_value=0,
                            id="tile-size-input",
                            hx_post="/parameter-updated",
                            hx_trigger="change, click",
                            hx_target="this",
                            hx_swap="none",
                            **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"tile_size" })'}
                        ),
                        entry.number_input(
                            'Tile Overlap', 
                            current_value=current_settings.active_parameters.tile_overlap,
                            maximum_value=2000,
                            minimum_value=0,
                            id="overlap-input",
                            hx_post="/parameter-updated",
                            hx_trigger="change, click",
                            hx_target="this",
                            hx_swap="none",
                            **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"tile_overlap" })'}
                            ),
                        entry.number_input(
                            'Doubles removal distance', 
                            current_value=current_settings.active_parameters.doubles_removal_distance,
                            maximum_value=2000,
                            minimum_value=0,
                            id="doubles-removal-input",
                            hx_post="/parameter-updated",
                            hx_trigger="change, click",
                            hx_target="this",
                            hx_swap="none",
                            **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"doubles_removal_distance" })'}
                            ),
                        cls="flex flex-row h-40 items-center justify-evenly",
                    ),
                    cls="flex flex-col",
                    id="split-0",
                    x_data="{ regionSize: 400 }"
                ),
                Div(
                    sidebar(),
                    id="split-1",
                    cls="flex flex-col min-w-fit"
                ),
                cls="flex grow",
            ),
            cls="flex flex-col h-screen",
            id="full-page-container", 
            style="opacity: 0;", 
        ),
    )

def sidebar():
    return (
        Div(
            Div(
                Svg(
                    G(
                        Image(
                            **{"xlink:href": get_base64_image(current_settings.image)},
                            x=str(-current_settings.preview_position[0]),
                            y=str(-current_settings.preview_position[1]),
                            transform=f"scale({current_settings.preview_scale})"
                        ),
                        id="preview-image-group"
                    ),
                    G(
                        *update_preview(),
                        id="circle-overlay-group",
                    ),
                    id="preview-svg",
                    cls="bg-gray-50 border border-gray-100",
                    style="""
                    width: 300px;
                    height: 300px;
                    """
                ),
                id="preview-container",
                cls="justify-center h-fit flex mt-5"
            ),
            scan_settings_menu(),
            Div(
                Button(
                    "Run Scan",
                    type="button",
                    hx_swap="outerHTML",
                    hx_post="/process_button_pressed",
                    cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-neutral-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 hover:text-neutral-600 hover:bg-neutral-100 h-12",
                ),
                cls="flex flex-col px-5 py-5",
            ),
            cls="flex flex-col flex-auto border-gray-50",
            style="max-height: calc((100vh / var(--dynamic-scale)) - (40px / var(--dynamic-scale)));",
            id="sidebar",
        ),
    )

def scan_settings_menu():
    return (
        Div(
            Div(
                entry.spinbox(
                    'Blur', minimum_value=1, maximum_value=21, increment_ammount=2, current_value=current_settings.active_parameters.blur, acceleration=100,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{'x-bind:hx-vals': 'JSON.stringify({ val: currentVal, name:"blur"})'},
                ),
                entry.spinbox(
                    'Minimum Distance', minimum_value=0, maximum_value=9999, current_value=current_settings.active_parameters.minimum_distance,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"minimum_distance" })'}
                ),
                entry.spinbox(
                    'Canny Upper Limit', minimum_value=0, maximum_value=999, current_value=current_settings.active_parameters.canny_upper_limit,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"canny_upper_limit" })'}
                ),
                entry.spinbox(
                    'Hough Threshold', minimum_value=0, maximum_value=999, current_value=current_settings.active_parameters.hough_threshold,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"hough_threshold" })'}
                ),
                entry.spinbox(
                    'Minimum Radius', minimum_value=0, maximum_value=9999, current_value=current_settings.active_parameters.minimum_radius,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"minimum_radius" })'}
                ),
                entry.spinbox(
                    'Maximum Radius', minimum_value=0, maximum_value=9999, current_value=current_settings.active_parameters.maximum_radius,
                    hx_post="/parameter-updated", hx_trigger="change, click", hx_target="#circle-overlay-group", hx_swap="innerHTML", hx_abort="true",
                    **{':hx-vals': 'JSON.stringify({ val: currentVal, name:"maximum_radius" })'}
                ),
                cls="w-full flex flex-col justify-start items-center content-center overflow-auto"
            ),
            selector.run_selector(current_settings=current_settings),
            id="scan-settings-menu",
            cls="flex flex-grow flex-col items-center justify-evenly overflow-y-auto h-1/3"
        ),

    )

@app.post("/new")
def new():
    file_path = webview.windows[0].create_file_dialog(
        webview.OPEN_DIALOG,
        file_types=["Image Files (*.jpg;*.png;*.tiff)"]
    )

    if isinstance(file_path, (tuple, list)):  # Handle tuple/list return values
        file_path = file_path[0] if file_path else None

    if file_path:
        file_path = Path(file_path).resolve()  # Convert to absolute path and normalize

    if file_path.exists():
        current_settings.image_path = str(file_path)
        current_settings.image = PILImage.open(file_path).convert("RGB")

    return (
        home(),
        Script("initialize_d3();"),
        Script("setTimeout(resize, 100);"),
    )


@app.post("/save_as")
def save_as():
    print('Saving file via Save As...')
    file_path = webview.windows[0].create_file_dialog(
        webview.SAVE_DIALOG,
        file_types=["JSON (*.json)  "]
        )
    if file_path:
        file_path = Path(file_path)
        with file_path.open("w") as f:
            # Export current settings as JSON for saving
            json.dump(current_settings, f, default=lambda o: o.__dict__, indent=2)
        print(f"Saved to {file_path}")
        return f"Saved to {file_path}"
    return "No file selected"

@app.post("/export_json")
def export_json():
    print('Exporting JSON...')
    file_path = webview.windows[0].create_file_dialog(
        webview.SAVE_DIALOG,
        file_types=["JSON (*.json)"]
    )

    if isinstance(file_path, (tuple, list)):  # Ensure correct handling
        file_path = file_path[0] if file_path else None
    
    if file_path:
        file_path = Path(file_path).resolve()  # Fix for Windows paths
        export_data = {
            "image_path": current_settings.image_path,
            "scans":{}
        }
        for scan in current_settings.scan_parameters:
            export_data["scans"][scan.scan_name] = {
                "scan_color":scan.scan_color,
                "blur":scan.blur,
                "minimum_distance":scan.minimum_distance,
                "canny_upper_limit":scan.canny_upper_limit,
                "hough_threshold":scan.hough_threshold,
                "minimum_radius":scan.minimum_radius,
                "maximum_radius":scan.maximum_radius,
                "tile_size":scan.tile_size,
                "tile_overlap":scan.tile_overlap,
                "doubles_removal_distamce":scan.doubles_removal_distance,
                "detected_circles":[{'x':int(i[0]), 'y':int(i[1]), 'radius':int(i[2])} for i in scan.detected_circles if scan.detected_circles is not np.empty]
            }
        
        
        if isinstance(file_path, (tuple, list)):  # Ensure correct handling
            file_path = file_path[0] if file_path else None

        if file_path:
            file_path = Path(file_path).resolve()
            with file_path.open("w") as f:
                json.dump(export_data, f, indent=2)
            print(f"Saved to {file_path}")
            return f"Saved to {file_path}"
        return "No file selected"

import numpy as np
import csv

@app.post("/export_csv")
def export_csv():
    print("Exporting CSV...")

    file_path = webview.windows[0].create_file_dialog(
        webview.SAVE_DIALOG,
        file_types=["CSV (*.csv)"]
    )

    if isinstance(file_path, (tuple, list)):  # Ensure correct handling
        file_path = file_path[0] if file_path else None

    if file_path:
        file_path = Path(file_path).resolve()  # Fix for Windows paths
        with file_path.open("w", newline="") as f:

            writer = csv.writer(f)

            for scan in current_settings.scan_parameters:
                # --- Write Scan Header ---
                writer.writerow([f"# Scan: {scan.scan_name}"])
                writer.writerow(["scan_name", "scan_color", "blur", "minimum_distance", "canny_upper_limit",
                                 "hough_threshold", "minimum_radius", "maximum_radius", "tile_size",
                                 "tile_overlap", "doubles_removal_distance"])

                writer.writerow([
                    scan.scan_name,
                    scan.scan_color,
                    scan.blur,
                    scan.minimum_distance,
                    scan.canny_upper_limit,
                    scan.hough_threshold,
                    scan.minimum_radius,
                    scan.maximum_radius,
                    scan.tile_size,
                    scan.tile_overlap,
                    scan.doubles_removal_distance
                ])

                # --- Write a blank line for separation ---
                writer.writerow([])

                # --- Write Detected Circles Section ---
                writer.writerow(["x", "y", "radius"])

                if isinstance(scan.detected_circles, np.ndarray) and scan.detected_circles.size > 0:
                    for circle in scan.detected_circles:
                        writer.writerow([int(circle[0]), int(circle[1]), int(circle[2])])

                # --- Another blank line to separate scans ---
                writer.writerow([])

        print(f"CSV exported to {file_path}")
        return f"CSV exported to {file_path}"

    return "No file selected"

@app.post("/open")
def open_file():
    # Use the main window's dialog to open a file.
    file_path = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG)
    print("Selected file:", file_path)
    return file_path if file_path else "No file selected"

@app.post("/add_scan")
def add_scan():
    print('Adding scan...')
    print('Current settings:', current_settings.active_parameters.scan_name)
    new_scan = copy.copy(current_settings.active_parameters)
    new_scan.scan_name = next(current_settings.scan_name_gen)
    current_settings.scan_parameters.append(new_scan)
    current_settings.active_parameters = new_scan
    return sidebar()

@app.post("/remove_scan")
def remove_scan():
    print('Removing scan...')
    print('Current settings:', current_settings.active_parameters.scan_name)
    current_settings.scan_parameters = [
        i for i in current_settings.scan_parameters if i.scan_name != current_settings.active_parameters.scan_name
    ] or [current_settings.active_parameters]
    current_settings.active_parameters = current_settings.scan_parameters[-1] if current_settings.scan_parameters else current_settings.active_parameters
    return sidebar()

@app.post("/select_scan")
def select_scan(name: Optional[str] = None):
    preview_position = current_settings.preview_position
    current_settings.active_parameters = next((i for i in current_settings.scan_parameters if i.scan_name == name), None)
    current_settings.preview_position = preview_position
    return sidebar()

@app.post("/update_color")
def update_color(color: Optional[str] = None, name: Optional[str] = None):
    if color and name:
        scan = next((i for i in current_settings.scan_parameters if i.scan_name == name), None)
        scan.scan_color = color
    return sidebar()

@app.post("/update_name")
def update_name(new_name: Optional[str] = None, name: Optional[str] = None):
    print('Updating name:', new_name, name)
    if new_name and name:
        scan = next((i for i in current_settings.scan_parameters if i.scan_name == name), None)
        scan.scan_name = new_name
    return sidebar()

@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
    return FileResponse(f'{fname}.{ext}')

@app.post("/parameter-updated")
def parameter_updated(val: Optional[int] = None, name: Optional[str] = None):
    if val and name:
        setattr(current_settings.active_parameters, name, val)
    return update_preview()

@app.post("/process_button_pressed")
def process_button_pressed():
    return (
        Button(
            "Processing Image",
            Div(
                hx_post="/process_image",
                hx_swap="innerHTML",
                hx_trigger="load",
                hx_target="#circle-overlay-main",
            ),
            Div(cls="p-2"),
            Svg(
            ft_path(d='M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z', opacity='.25'),
            ft_path(d='M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z'),
            xmlns='http://www.w3.org/2000/svg',
            viewbox='0 0 24 24',
            aria_hidden='true',
            cls='size-5 fill-on-surface motion-safe:animate-spin dark:fill-on-surface-dark'
            ),
            type="button",
            hx_post="/cancel_button_pressed",
            hx_swap="outerHTML",
            hx_trigger="click",
            id="loading-button",
            cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-red-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 h-12",
        ),
    )

@app.post("/image-returned-success")
def image_returned_success():
    print('Returning button...')
    return (
        Button(
            "Run Scan",
            type="button",
            hx_swap="outerHTML",
            hx_post="/process_button_pressed",
            cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-neutral-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 hover:text-neutral-600 hover:bg-neutral-100 h-12",
        ),
    )


@app.post("/process_image")
def process_image():
    global tile_processor_instance
    global processing_active
    print("Processing image...")

    # Reset the cancellation event at the start of processing
    cancel_event.clear()  
    processing_active = True  

    all_cirlces_overlay = []
    tile_processor_instance = TileProcessor(
        np.array(current_settings.image.convert('L')), 
        tile_size=current_settings.active_parameters.tile_size, 
        overlap=current_settings.active_parameters.tile_overlap
    )

    try:
        for i in current_settings.scan_parameters:
            circles = []
            detected_circles = tile_processor_instance.process_tiles_parallel(
                CircleDetector.detect_circles,
                blur=i.blur,
                dp=1,
                min_dist=i.minimum_distance,
                canny_upper=i.canny_upper_limit,
                hough_threshold=i.hough_threshold,
                min_radius=i.minimum_radius,
                max_radius=i.maximum_radius
            )

            # If processing was canceled, return early with full cleanup
            if cancel_event.is_set():
                print("🔴 Processing stopped due to cancellation.")
                processing_active = False  # 🔹 Only set False after cleanup
                return Div()  

            i.detected_circles = detected_circles
            circles.append(detected_circles)
            print(circles)

            circle_svg_overlay = [
                [SvgInb(Circle(cx=j[0], cy=j[1], r=j[2], fill="none", stroke=i.scan_color, stroke_width=5, stroke_opacity="1"),
                          height=f"{tile_processor_instance.height}px",
                          width=f"{tile_processor_instance.width}px")
                 for j in tile]
                for tile in circles
            ]
            all_cirlces_overlay.append(circle_svg_overlay)

    except Exception as e:
        print(f"⚠️ Error during processing: {e}")
    finally:
        processing_active = False  # 🔹 Make sure we properly mark processing as stopped

    return [j for i in all_cirlces_overlay for j in i] + [
        Div(hx_post="/image-returned-success", hx_swap="outerHTML", hx_trigger="load", hx_target="#loading-button")
    ]



@app.post("/cancel_button_pressed")
def cancel_processing_request():
    """trigger cancel process"""
    return (
        Button(
            "Stopping...",
            type="button",
            hx_trigger="load",
            hx_swap="outerHTML",
            hx_post="/cancel_success",
            cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-red-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 hover:text-neutral-600 hover:bg-neutral-100 h-12",
        ),
    )


@app.post("/cancel_success")
def cancel_success():
    """Cancel the currently running image processing and return as soon as it stops."""
    
    print("Cancel request received. Waiting for processing to stop...")

    # Set the cancellation event
    cancel_event.set()

    # Wait until processing_active is False
    while processing_active:
        time.sleep(0.1)  # Shorter sleep for faster response

    print("Processing has stopped. Returning button.")

    return (
        Button(
            "Run Scan",
            type="button",
            hx_swap="outerHTML",
            hx_post="/process_button_pressed",
            cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-neutral-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 hover:text-neutral-600 hover:bg-neutral-100 h-12",
        ),
    )


@app.post("/image_clicked")
def image_clicked(preview_width: Optional[int] = None, preview_height: Optional[int] = None,
                  region_x: Optional[float] = None, region_y: Optional[float] = None,
                  tile_size: Optional[int] = None, image_path: Optional[str] = None):
    current_settings.preview_position = (region_x or current_settings.preview_position[0],
                                           region_y or current_settings.preview_position[1])
    current_settings.active_parameters.tile_size = tile_size or current_settings.active_parameters.tile_size
    if preview_width or preview_height:
        current_settings.preview_size = max(preview_width, preview_height)
    return update_preview()

def update_preview():
    scale = float(current_settings.preview_size) / float(current_settings.active_parameters.tile_size)
    current_settings.preview_scale = scale
    cropped_img = current_settings.image.convert('L').crop((
        current_settings.preview_position[0],
        current_settings.preview_position[1],
        current_settings.preview_position[0] + current_settings.active_parameters.tile_size,
        current_settings.preview_position[1] + current_settings.active_parameters.tile_size
    ))
    circle_svg_overlay = []
    for i in current_settings.scan_parameters[::-1]:
        circles = CircleDetector.detect_circles(
            image=np.array(cropped_img),
            blur=i.blur,
            min_dist=i.minimum_distance,
            canny_upper=i.canny_upper_limit,
            hough_threshold=i.hough_threshold,
            min_radius=i.minimum_radius,
            max_radius=i.maximum_radius,
            timeout=5
        )
        [circle_svg_overlay.append(SvgInb(
            Circle(cx=j[0]*scale, cy=j[1]*scale, r=j[2]*scale,
                   fill="none", stroke=i.scan_color, stroke_width=3, stroke_opacity="0.7")
        )) for j in circles]
    print('circles -->', circles)
    return circle_svg_overlay

os.environ["QT_QPA_PLATFORM"] = "wayland"

def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            time.sleep(0.5)  # Wait before retrying
    raise Exception("Server did not start in time.")

# Replace your run_server function with this:
def run_server():
    """Run FastAPI's Uvicorn server in a separate thread with proper shutdown."""
    global server
    
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    
    server_thread = threading.Thread(
        target=server.run,
        daemon=True
    )
    server_thread.start()

    # Wait until the server is available before continuing
    time.sleep(0.5)  # Give the server time to start

    try:
        wait_for_server(f"http://127.0.0.1:{PORT}")
        if HAS_PYI_SPLASH:
            pyi_splash.close()
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)

# Add this function to handle window closing
def on_window_close():
    """Handle the window close event to properly shut down the application."""
    print("Window closing, shutting down server...")
    if server:
        server.should_exit = True
    
    # Schedule the actual exit to happen after webview has a chance to clean up
    threading.Timer(0.5, lambda: os._exit(0)).start()

# Modify your main block
if __name__ == '__main__':
    # Only apply on Windows and only in main process
    freeze_support()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    try:
        wait_for_server(f"http://127.0.0.1:{PORT}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Create window with the close callback
    window = webview.create_window(
        "Hough Scan", 
        f"http://127.0.0.1:{PORT}", 
        width=1200, 
        height=800, 
        zoomable=True
    )
    
    # Register the close event handler
    window.events.closed += on_window_close
    
    # Add a SIGINT handler (for Ctrl+C)
    def handle_sigint(sig, frame):
        print("Ctrl+C detected, shutting down...")
        on_window_close()
    
    signal.signal(signal.SIGINT, handle_sigint)
    
    webview.start()