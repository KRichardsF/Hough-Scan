import io
import base64
from fasthtml.common import Div, Svg, Button
from fasthtml.components import Image, G

def get_base64_image(image, format="JPEG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"

def main_canvas(current_settings):
    return(
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
        )
    )