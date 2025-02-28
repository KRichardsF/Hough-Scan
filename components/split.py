from fasthtml.common import Script, Style

def split_pane(split_ids:list, min_size=2, max_size='', gutter_size=10, snap_offset=30, drag_interval=1, gutter_align='', gutter_colour='#f9fafb', sizes:list=[]):
    """ requires fluid_spinbox.js to be imported"""
    return(
        Script(
            f"""
            Split([{', '.join([f'"#{i}"' for i in split_ids])}], {{
                minSize: {min_size},
                maxSize: {max_size or '""'},
                sizes: [{', '.join([str(i) for i in sizes])}],
                gutterAlign: "{gutter_align or ''}",
                gutterSize: {gutter_size},
                snapOffset: {snap_offset},
                dragInterval: {drag_interval},
            }})
            """,
            type="module"
        ),
        Style(
        f""""
        .split {{
            display: flex;
            flex-direction: row;
        }}

        .gutter {{
            background-color: {gutter_colour};
            background-position: 50%;
            opacity: 0; /* Start with the gutter being invisible */
            transition: opacity 0.1s ease-in-out; /* Smooth transition for the fade-in effect */
        }}

        .gutter:hover {{
            opacity: 0.6; /* Fully visible on hover */
        }}

        .gutter.gutter-horizontal {{
            cursor: col-resize;
        }}
        """
        )
    )
