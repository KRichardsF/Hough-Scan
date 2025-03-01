
<img src="./static/icons/icon.svg" width="15%" height="15%"><h1> Hough Scan </h1> 
<a href="https://doi.org/10.5281/zenodo.4783636"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.4783636.svg" alt="DOI"></a>

<p align="left">
Application for detection and data extraction of circular objects, such as emulsion droplets, from microscopy images
  </p>
  
<h3> Contents </h3>
<ul> 
  <li><a href="#Installation_exe"> Installation (.exe file)
  <li><a href="#Installation_source"> Installation (from source)
  <li><a href="#User Guide"> User Guide
  <li><a href="#Planned Updates"> Planned Updates
  <li><a href="#Examples"> Examples
  <li><a href="#Theory"> Theory
  <li><a href=""> Changelog
  <li><a href=""> Known Issues
    </ul>
  
 <h2><a name="Installation_exe"> Installation (.exe file)</a></h2>
 <h3> Windows </h3>
 <ul>
    <li> Download the latest zip file found <a href="https://github.com/KRichardsF/Hough-Scan/releases">here</a> 
    <li> Extract the file to an appropriate folder (i.e c:program files/hough-scan)
    <li> (optional) copy and paste a shortcut for "houghscan.exe" to your desktop/start menu
    <li> Double click "houghscan.exe" to run the program
 </ul>
 
<h2><a name="Installation_source"> Installation (from source)</a></h2>
<h3> Winows / linux </h3>
<ul>
  <li>Check that you have python installed</li>
  <li>Clone files using <code>git clone https://github.com/KRichardsF/Hough-Scan/</code> or by downloading them from web browser.
   <li>Navigate to the build folder and install dependenceies using <code>pip install -r requirements.txt</code>
<br>
   <li>Navigate to Main Hough-Scan directory in terminal and run:
   <code>Python main.py</code>
</ul>

  
<h2><a name="User Guide"> User Guide </a></h2>
<img src="./Readme_Images/Screenshot.png" width="50%" height="50%">
<ul>
  <li> Step 1: Run the program
  <li> Step 2: Open an image
  <li> Step 3: Set the tile size depending on how densely populated with circles your image is. Make sure that the 'number of tiles' X 'size of tiles' is greater than the image size
  <li> step 4: click an area of interest on the image and set the parameters on the right hand side. Start with 'Hough Threshold' and 'Canny Upper' at a higher value (60+) if you have a complex image. Setting an Upper and lower radius will speed up processing time.
  <li> Step 5: Click run. (results may take some time) 
  <li> Step 6: Press the icons adjacent to the run button to get a histogram and list of data
  <li> Step 7 (optional): Add additional runs by pressing the + or - button
</ul>

<h2><a name="Planned Updates"> Planned Updates </a></h2>
<ul>
<li> Ability to abort acquisitions
<li> Loading bar
<li> Show circle size histogram
  </ul>



<h2><a name="Examples"> Examples </a></h2>
<ul>
<li> Kieran Richards, Ella Comish, Rachel Evans, 
 <i>Computer vision for high-throughput analysis of Pickering emulsions</i>, Soft Matter, 2025, <a href="https://pubs.rsc.org/en/content/articlelanding/2025/sm/d4sm01252f"> DOI: 10.1039/D4SM01252F </a>
</a></li>


</ul>

<h2><a name="Theory"> Theory </a></h2>
<p> For more information on the image manipulation processes, please visit https://opencv.org/ . Below we have summarised some of the processes performed by the OpenCV library in order to give the user a better idea what each of the parameters used in this software do. </p>
  
  
  <p align="left">
  Hough Scan uses the following techniques to process an image: greyscale conversion, blur, sobel operation and canny edge detection followed by the circle Hough-transform.
  </p>
<h3> Kernel Convolution </h3>
<p> Blur and Sobel are both kernel convolution processes. For each pixel in the image (red square) the neighbouring pixels (green square) are added using a weighting which is determined by the kernel (3x3 matrix - greek letters in this case). The output is then often normalised. The "Blur" parameter adjusts the number of pixels used in blurring </p>
<img src="./Readme_Images/Kernel_Convolution.png" width="50%" height="50%"><br>
<img src="./Readme_Images/Kernel_Equation.png" width="15%" height="15%">


<h3> Sobel Operation </h3>
<p> The Sobel operation is an example of a kernel convolution process used for edge detection. It is applied in both the x and y direction independently and allows the calculation of angular information as shown by the below figure. This information is then used in the next process - canny edge detection. </p>
<br>
<img src="./Readme_Images/Sobel_Operation.png" width="50%" height="50%">
<img src="./Readme_Images/Sobel_Equation.png" width="70%" height="70%">

<h3> Canny Edge Detection </h3>
<p> Canny edge detection uses two thresholds (primary and secondary). A line is drawn in the direction of the 'edge' values above the primary threshold are retained and values below are removed. If however, a value is below the primary threshold but above the secondary threshold <b> and </b> is also connected to a point above the primary threshold by pixel tracing (i.e. without dipping below the secondary threshold) the value is retained. The "Canny Upper" parameter sets the primary threshold and the secondary threshold is automatically set.</p> 
<br>
<img src="./Readme_Images/Canny_Edge.png" width="60%" height="60%">

<h3> Circle Hough Transform </h3> 
<p> At this stage the image has been refined to a set of thin white lines/circles on a black background. The circle Hough-transform will scan across the image until it finds a white pixel. For each pixel it will draw a circle of radius r (where r is an ever-increasing value upon each pass of the image and is set between two limits) is drawn using the equation for a circle.</p>
<br>
<img src="./Readme_Images/Circle_Equation.png" width="20%" height="20%">
<br>
<p> the circles are added to an 'accumulator image'. If the radii of the drawn circles match the radii of circles in the image, a bright spot will be seen indicating the centre of the circle. The "Hough Threshold" parameter is used to determine at which value a bright spot is considered a true centre of a circle. The "Min distance" parameter will set a minimum distance between circle centres, the "Min and Max Radius" will determine the values of r that are considered.</p>
  
<img src="./Readme_Images/Circle_Hough.png" width="50%" height="50%">
  
 <h3> Tiling </h3> 
 <p> due to the complexity of many microscopy images (with i.e. more than 100 circular objects) it is convenient to tile the images, allowing for redundancy at the boundary by removing duplicate coordinates. The size of tiles used, the overlap and the distance to remove duplicates may be altered using the "Tile Size, Overlap and Doubles Removal Dist." parameters.</p>


<h2><a name="Changelog"> Changelog </a></h2>
<ul>
  <li> 28FEB25: Reconfigured software with web UI for better compatibility
  <li> 07AUG20: Export as JSON file
  <li> 07AUG20: Executable Version for Windows
  <li> 07AUG20: Tile by Percentage Overlap added
  <li> 07AUG20 Separate tile sizes for different runs
  <li> 8JUL20: uploaded early dev build
</ul>

<h2><a name="Known Issues"> Known Issues </a></h2>
<ul>
  <li> Using .exe, Windows security treats file as threat.<br>
  (To resolve, right-click HoughScan.exe > properties > security > check 'unblock'> press apply)
  <li> Using .exe, startup time is slow (>10s).
  
  
</ul>
