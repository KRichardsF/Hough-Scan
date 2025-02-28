from fasthtml.common import *
from components import button, menu, split, entry

headers = (
    Script(src="https://cdn.tailwindcss.com"),
    Script(src="https://unpkg.com/alpinejs", defer=True),
    Script(src="https://d3js.org/d3.v7.min.js", defer=True),
    Script(src="https://cdnjs.cloudflare.com/ajax/libs/split.js/1.6.0/split.min.js", defer=True),
    Script(src="scripts/fluid_spinbox.js"),
    Script(src="scripts/d3_image_canvas.js", type="module"),
    Link(rel="icon", type="image/x-icon", href="/images/favicon.ico"),
)
app = FastHTML(hdrs=headers)

@app.get("/")
def home():
    return (
            Title("Hough Scan"),
            Div(
                # Main menu
                menu.top_menu(
                    menu.menu_item(
                        'File',
                        menu.menu_selection('Save as...',  keys=['Alt','Shift','D'], hx_swap='none', hx_post='/save_as'),
                        menu.menu_selection('Open', keys='o', hx_swap='none', hx_post='/open'),
                        menu.submenu(
                            'More...',
                            menu.submenu_selection('Json export'),
                            menu.submenu_selection('CSV Export')
                        ),
                    ),
                    menu.menu_item('Edit'),
                    menu.menu_item('View'),
                ),
                # Page Content
                Div(
                    split.split_pane(["split-0", "split-1"], gutter_size=4, max_size=None, min_size=0, gutter_colour='#7040c8', sizes=[95,5]),
                    # Main Canvas
                    Div(
                        Div(id="image-container", cls=""),
                        id = "split-0",
                        cls = ""
                    ),
                    # Sidebar
                    Div(
                        Div(
                            id="preview-container",
                            # cls="h-1/6 aspect-w-1 aspect-h-1 bg-sky-600 w-full"
                            # cls="h-300 w-300"
                        ),
                        Div(
                            entry.spinbox('Blur', minimum_value=0, maximum_value=500, current_value=200, acceleration=100),
                            entry.spinbox('Minimum Distance'),
                            entry.spinbox('Canny Upper Limit'),
                            entry.spinbox('Hough Threshold'),
                            entry.spinbox('Minimum Radius'),
                            entry.spinbox('Maximum Radius'),
                            cls="w-5/6 flex flex-col justify-center items-center content-center shrink-0 grow"
                        ),
                        id="split-1",
                        cls = "relative flex-col px-5 justify-start w-auto h-100 items-between border-gray-50 flex items-center min-w-fit"

                    ),
                cls = "flex grow",
                ),
            cls="flex flex-col h-screen"
            ),
        )

@app.post("/save_as")
def save_as():
    print('Saving file...')

@app.post("/open")
def open():
    print("Opening file...")

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')


serve()
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// Create a responsive SVG container
const container = d3.select("#image-container");

const svg = container
  .append("svg")
  .style("width", "100%")
  .style("height", "100%");

const g = svg.append("g");

// Load the image
const img = new Image();
img.onload = function () {
  const imgAspectRatio = img.width / img.height;

  // Set up zoom behavior
  const zoom = d3.zoom().scaleExtent([0.95, 100]).on("zoom", zoomed);

  svg.call(zoom);

  // Add the image to the SVG
  g.append("image")
    .attr("xlink:href", "test-image.jpg")
    .attr("width", "100%")
    .attr("height", "100%");

  function zoomed(event) {
    g.attr("transform", event.transform);
  }

  // Resize function
  function resize() {
    const containerWidth = container.node().clientWidth;
    const containerHeight = container.node().clientHeight;
  }

  // Initial resize
  resize();

  // Resize on window resize
  window.addEventListener("resize", resize);

  // Zoom buttons
  d3.select("#zoom-in").on("click", () =>
    svg.transition().call(zoom.scaleBy, 1.2),
  );
  d3.select("#zoom-out").on("click", () =>
    svg.transition().call(zoom.scaleBy, 0.8),
  );
  d3.select("#reset").on("click", () =>
    svg.transition().call(zoom.transform, d3.zoomIdentity),
  );
  svg.on("click", function (event) {
    const [x, y] = d3.pointer(event, this);
    const transform = d3.zoomTransform(svg.node());
    const imageX = (x - transform.x) / transform.k;
    const imageY = (y - transform.y) / transform.k;
    console.log(imageX, imageY);
    // Update htmx values dynamically
    svg.attr("hx-vals", JSON.stringify({ imageX: imageX.toFixed(2), imageY: imageY.toFixed(2) }));
  });
};

img.src = "test-image.jpg";
