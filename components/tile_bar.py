from fasthtml.common import Div
from components import entry

def tile_bar(current_settings):
        return(
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
    )