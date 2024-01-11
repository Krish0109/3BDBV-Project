
# Paint Application with Gesture Recognition




## Overview

This Python script implements a paint application with gesture recognition using the MediaPipe library. The application captures video from the webcam, detects hand gestures, and allows users to draw on a canvas using different colors based on specific hand gestures.

## Features

### Gesture Recognition:
 * Utilizes the MediaPipe library for hand tracking.
 * Classifies hand gestures based on the angles between finger tips.
 * Recognizes gestures such as closed fist, open palm, thumb up/down, pointing up, etc.

 ### Canvas Drawing:
 * Users can draw on a canvas using different colors.
 * Color assignment is based on specific hand gestures.

 ### Real-time Feedback:
 * Live video feed from the webcam is displayed alongside the canvas.
 * Gesture recognition results are displayed in the Tkinter GUI.

 ## Dependencies

 * OpenCV (cv2): Computer vision library for webcam access.
* MediaPipe (mediapipe): Hand tracking library.
* Tkinter: GUI library for creating the application.
* PIL (Pillow): Image processing library for working with images.
* NumPy: Library for numerical operations.

## Usage

1. Install the required dependencies:
```bash
  pip install opencv-python mediapipe pillow numpy
```
2. Run the script:
```bash
python gesture_recognizer.py
```
3. Interact with the paint application using hand gestures.


## Gesture Labels
The script uses a dictionary to map numerical labels to specific hand gestures:

* 0: "Unknown"
* 1: "Closed Fist"
* 2: "Open Palm"
* 3: "Pointing Up"
* 4: "Thumb Down"
* 5: "Thumb Up"
* 6: "Victory"

## Acknowledgments
This script is based on the use of MediaPipe for hand tracking. Special thanks to the contributors of the open-source libraries used in this project.

## Troubleshooting:
* Does not work on Ubuntu 20.04 or earlier!
* python: from 3.8.x to 3.11.x
* PIP: version 20.3+
