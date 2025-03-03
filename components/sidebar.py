from fasthtml.common import Div, Svg, Button
from fasthtml.components import Defs, ClipPath, Rect, Image, G
from components import selector, entry
import io
import base64


def get_base64_image(image, format="JPEG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"

def sidebar(current_settings, update_preview):
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
            scan_settings_menu(current_settings),
            Div(
                Button(
                    "Run Scan",
                    type="button",
                    hx_swap="outerHTML",
                    hx_post="/process_button_pressed",
                    cls="inline-flex items-center justify-center px-4 py-2 text-sm font-medium tracking-wide transition-colors duration-100 rounded-md text-neutral-500 bg-neutral-50 focus:ring-2 focus:ring-offset-2 focus:ring-neutral-100 hover:text-neutral-600 hover:bg-neutral-100 h-12",
                ),
                cls="flex flex-col px-5 pb-3",
            ),
            cls="flex flex-col flex-auto border-gray-50",
            style="max-height: calc((100vh / var(--dynamic-scale)) - (40px / var(--dynamic-scale)));",
            id="sidebar",
        ),
    )

def scan_settings_menu(current_settings):
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
