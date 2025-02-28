function initialize_d3() {
  // Create a responsive SVG container
  const container = d3.select("#image-container");
  const svg = container
    .select("#user-image")
    .style("width", "100%")
    .style("height", "100%");

  // Select the existing group element to hold the image
  const g = d3.select("#main-canvas");

  // Select the existing image instead of creating a new one
  const img = d3.select("#loaded-image");
  const imagePath = img.attr("href"); // Get image path from existing image

  // Set up zoom behavior
  const zoom = d3.zoom().on("zoom", zoomed);
  svg.call(zoom);

  // Zoom event handler
  function zoomed(event) {
    g.attr("transform", event.transform);
  }

  // Resize function to maintain image aspect ratio within the container
  window.resize = function resize() {
    const imgNode = img.node();
    const imgWidth = imgNode ? imgNode.getBBox().width : 0;
    const imgHeight = imgNode ? imgNode.getBBox().height : 0;
    // Get the container dimensions
    console.log("PART 1");
    const containerWidth = container.node().clientWidth;
    const containerHeight = container.node().clientHeight;
    console.log("part 2 container", containerWidth, containerHeight);
    // Calculate the scale factor to fit the entire image
    // check the display scale according to media queries
    const rootStyles = getComputedStyle(document.documentElement);
    const scaleFactor =
      parseFloat(rootStyles.getPropertyValue("--dynamic-scale")) || 1;
    console.log(scaleFactor);
    console.log("part 3");
    const scale = Math.min(
      containerWidth / imgWidth,
      containerHeight / imgHeight,
    );
    console.log("part 4: scale", scale);
    // Calculate the translation to center the image
    const translateX = (containerWidth - imgWidth * scale) / 2;
    const translateY = (containerHeight - imgHeight * scale) / 2;
    console.log("part 5", translateX, translateY, imgWidth, imgHeight);
    // Apply the initial zoom transform to center and fit the image
    const initialTransform = d3.zoomIdentity
      .translate(translateX, translateY)
      .scale(scale);

    svg.transition().duration(0).call(zoom.transform, initialTransform);
    document.getElementById('full-page-container').style.opacity = '1';
  };

  // Resize the image when the window is resized
  window.addEventListener("resize", resize);

  // Track the current mouse position relative to the SVG
  let currentMousePosition = { x: 0, y: 0 };
  svg.on("mousemove", function (event) {
    currentMousePosition = d3.pointer(event, svg.node());
  });

  // Function to get the current mouse coordinates relative to the image
  getCoords = function () {
    const [x, y] = currentMousePosition;
    const transform = d3.zoomTransform(svg.node());

    const imageX = (x - transform.x) / transform.k;
    const imageY = (y - transform.y) / transform.k;

    console.log(`Image Coordinates: (${imageX}, ${imageY})`);
    return { x: imageX, y: imageY };
  };

  // Separate function for updating the preview
  function updatePreview(coords, imagePath) {
    // Define the size of the region to display in the preview
    const tileSize = Alpine.$data(
      document.getElementById("tile-size-input"),
    ).currentVal;

    // Calculate the region's top-left corner
    const regionX = coords.x - tileSize / 2;
    const regionY = coords.y - tileSize / 2;

    // Get scale factor from CSS
    const rootStyles = getComputedStyle(document.documentElement);
    const scaleFactor =
      parseFloat(rootStyles.getPropertyValue("--dynamic-scale")) || 1;

    // Get bounding box in CSS pixels (already affected by scaling)
    const rawBBox = d3.select("#preview-svg").node().getBoundingClientRect();

    // Correct values by reversing the scale
    const previewBBox = {
      x: rawBBox.x / scaleFactor,
      y: rawBBox.y / scaleFactor,
      width: rawBBox.width / scaleFactor,
      height: rawBBox.height / scaleFactor,
    };

    // Select the image preview group
    const previewGroup = d3.select("#preview-image-group");

    // Remove any circles drawn into the the circle-overlay node
    d3.select("#circle-overlay-group").html("");

    // Adjust the preview image
    previewGroup
      .select("image")
      .attr("x", -regionX) // Offset to focus on the clicked region
      .attr("y", -regionY) // Offset to focus on the clicked region
      .attr("transform", `scale(${previewBBox.width / tileSize})`); // Scale the image to fill the preview area

    // Send the base64-encoded image to the server using HTMX
    htmx.ajax("POST", "/image_clicked", {
      values: {
        region_x: regionX,
        region_y: regionY,
        tile_size: tileSize,
        image_path: imagePath,
        preview_width: previewBBox.width,
        preview_height: previewBBox.height,
      },
      target: "#circle-overlay-group", // Target the group inside the preview SVG
      swap: "innerHTML", // Specify the swap strategy to replace the group content with server response
      abort: "true",
    });
  }

  // Update preview on image click
  g.on("click", function () {
    const coords = getCoords();
    updatePreview(coords, imagePath);
  });

  window.addEventListener("load", resize);

}

// Initialize everything
initialize_d3();
