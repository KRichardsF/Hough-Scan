<h1> Hough Scan </h1>

<p align="left">
Application for detection and data extraction of circular objects, such as emulstion droplets, from microscopy images
  </p>
  
<h3> Contenets </h3>
<ul> 
  <li><a href="#Installation"> Installation
  <li><a href=""> Dependencies
  <li><a href=""> User Guide
  <li><a href="#Theory"> Theory
  
  
 <h2><a name="Installation"> Installation (Developer Build)</a></h2>
  <p align="left">    

  <h3> linux </h3>
  <ul>
<li>Install dependencies.<br>
<li>Navigate to Hough-Scan directory in terminal and run:
  </p>
<code> Python3 houghscan.py </code>
<h3> Windows </h3>
<p> Hough Scan is created using GTK3+ which cannot be installed via pip command used for other packages, as such there are two main options if you wish to access the developer build </p>

<b> Option 1 (Install via MYSYS2) </b> 
<ul>
<li>Install Mysys2 and the packages required for GTK3+ by following the instructions here: <br>
https://www.gtk.org/docs/installations/windows/ <br>
<li>Install all other dependencies <br>
<li>Run via mysys2 terminal by navigating to Hough-Scan directory and run:
<code> Python3 houghscan.py </code>

<b> Option 2 Install via (WSL2)</b> 
<ul>
<li> Install WSL and install dependencies for linux distro. Guide: https://wiki.ubuntu.com/WSL <br>
GUI support is comming in a future update (https://devblogs.microsoft.com/commandline/the-windows-subsystem-for-linux-build-2020-summary/#wsl-gui)
but for now you will need to enable support via X server. (in more detail at https://wiki.ubuntu.com/WSL)<br>
<li> Follow linux installation instructions.</p>
<li> Navigate to Hough-Scan directory in terminal and run
<code> Python3 houghscan.py </code>

<h2><a name="Theory"> Theory </a></h2>
  <p align="left">
Hough Scan uses the following processes on an image
  </p>
<img src="./Readme_Images/Sobel.png" width="50%" height="50%">
