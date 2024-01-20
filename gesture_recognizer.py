import cv2
from collections import deque
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk
import threading
import math
import mediapipe as mp
import numpy as np
import sys, os, signal
import pyttsx3
from datetime import datetime

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Create a global variable to store the reference to the PhotoImage object
photo_reference = None

# Create a hands model instance
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define gesture labels
gesture_labels = {
    0: "Unknown",
    1: "Closed_Fist",
    2: "Open_Palm",
    3: "Pointing_Up",
    4: "Thumb_Down",
    5: "Thumb_Up",
    6: "Victory",
}

# Use OpenCV’s VideoCapture to start capturing from the webcam.
cap = cv2.VideoCapture(0)
paintWindow = np.zeros((471, 636, 3)) + 255
paintWindow_panel = np.zeros((65, 636, 3)) + 255

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)

def say_text(text):    
    while engine._inLoop:
        pass
    engine.say(text)
    engine.runAndWait()

image_saved = False

def image_save_called():
    global image_saved
    image_saved = True

def save_image(image_input):
    global image_saved

    now = datetime.now()
    current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
    cv2.imwrite('paint_window_'+current_time+'.png', image_input) 

    # image_input.save("img1.png","PNG")
    image_saved = False

def speak_gesture(gesture_label):
    global colorIndex
    speech_text = "Selected Color: " + str(colors_strings[colorIndex])
    threading.Thread(target=say_text, args=(speech_text, )).start()

def update_label(result_text):
    global label_panel
    label_panel.configure(text = result_text)

def calculate_angle(point1, point2):
    angle_rad = math.atan2(point2.y - point1.y, point2.x - point1.x)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def update_canvas(frame):
    global photo_reference
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    img = ImageTk.PhotoImage(image=img)

    # Display the frame in the Tkinter applet
    canvas.config(width=img.width(), height=img.height())
    canvas.img = img
    canvas.create_image(0, 0, anchor=NW, image=img)

    # Store a reference to the PhotoImage object
    photo_reference = img

def classify_gesture(hand_landmarks):
    # Extract landmarks for specific fingers
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    # Calculate angles between finger tips
    angle_thumb_index = calculate_angle(thumb_tip, index_finger_tip)
    angle_index_middle = calculate_angle(index_finger_tip, middle_finger_tip)
    angle_middle_ring = calculate_angle(middle_finger_tip, ring_finger_tip)
    angle_ring_pinky = calculate_angle(ring_finger_tip, pinky_tip)
    angle_thumb_pinky = calculate_angle(thumb_tip, pinky_tip)
    # Print angles for each frame
    #print(f"Thumb-Index Angle: {angle_thumb_index}")
    #print(f"Index-Middle Angle: {angle_index_middle}")
    #print(f"Middle-Ring Angle: {angle_middle_ring}")
    #print(f"Ring-Pinky Angle: {angle_ring_pinky}")
    #print(f"Thumb-Pinky Angle: {angle_thumb_pinky}")

    # Adjust these thresholds based on your specific angles
    if  -65 >= angle_thumb_index >= -100 and 80 <= angle_index_middle <= 105:
        return 3  # Pointing_Up
    elif 20 <= angle_thumb_index <= 60 and 110 <= angle_thumb_pinky <= 160:
        return 1  # Closed_Fist
    elif -90 >= angle_thumb_index >= -115 and -135 >= angle_index_middle >= -165:
        return 2  # Open_Palm
    elif 50 <= angle_thumb_index <= 90 and 60 <= angle_thumb_pinky <= 100:
        return 5  # Thumb_Up
    elif -80 >= angle_thumb_index >= -120 and -80 >= angle_thumb_pinky >= -120:
        return 4  # Thumb_Down
    elif -145 >= angle_index_middle >= -175 and 65 <= angle_middle_ring <= 105:
        return 6  # Victory
    else:
        return 0  # Unknown

# Convert OpenCV image to Tkinter format
def convert_to_tkinter(image, flip = False):
    if flip:
        image = cv2.flip(image, 1)    
    image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    return ImageTk.PhotoImage(image=image)


# Giving different arrays to handle color points of different colors
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# These indexes will be used to mark the points in particular arrays of specific color
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

# The kernel to be used for dilation purpose
kernel = np.ones((5, 5), np.uint8)

colors = [(230, 216, 173), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colors_strings = ["BLUE", "GREEN", "RED", "YELLOW"]
# colorIndex = 0

# Here is code for Canvas setup
paintWindow = np.zeros((471, 636, 3)) + 255
paintWindow = cv2.flip(paintWindow, 1)

paintWindow_panel = cv2.rectangle(paintWindow_panel, (40, 1), (140, 65), (0, 0, 0), 2)
paintWindow_panel = cv2.rectangle(paintWindow_panel, (160, 1), (255, 65), colors[0], -1)
paintWindow_panel = cv2.rectangle(paintWindow_panel, (275, 1), (370, 65), colors[1], -1)
paintWindow_panel = cv2.rectangle(paintWindow_panel, (390, 1), (485, 65), colors[2], -1)
paintWindow_panel = cv2.rectangle(paintWindow_panel, (505, 1), (600, 65), colors[3], -1)

cv2.putText(paintWindow_panel, "CLEAR", (50, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "Open Palm", (50, 53), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "BLUE", (170, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "Victory V", (170, 53), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "GREEN", (285, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "Thumb Up", (285, 53), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "RED", (400, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "Thumb Down", (400, 53), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "YELLOW", (515, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow_panel, "Closed Fist", (515, 53), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

def exitFunction():
    # Release the camera and all resources
    cap.release()
    cv2.destroyAllWindows()
    print ("Bye...")    
    try:
        root.destroy()
    except:
        pass
    try:
        print("from sys")
        sys.exit(0)
    except:
        pass
    try:
        print("from windows os")
        os._exit(0)
    except:
        pass
    try:
        print("from linux os")
        os.kill(os.getpid(), signal.SIGINT)
    except:
        pass

bg_color = 'orange'

splash_root = Tk()
splash_root.title("Air Canvas")
splash_root.geometry("900x700")
splash_root.configure(background=bg_color)

logo = Image.open('design_6.png')
logo_resized = logo.resize((100, 100))
logo = ImageTk.PhotoImage(logo_resized)

splash_label_logo = Label(splash_root, image=logo)
splash_label_logo.pack()

splash_label = Label(splash_root, text="Welcome to \nAir Canvas", font='times 20 bold', bg=bg_color)
splash_label.pack(pady=20)

splash_topic = Label(splash_root, text="Mensch-Roboter-Interaktion (HRI) mit Gestenerkennung: \n",font='times 20 bold', bg=bg_color )
splash_topic.pack(pady=20)

splash_topic_desc = Label(splash_root, text=" Mensch-Roboter-Interaktion (HRI) mit Gestenerkennung: \n Entwicklung von Systemen, die es Robotern ermöglichen, \n menschliche Gesten zu erkennen und darauf zu reagieren, um eine \n natürlichere Interaktion zu ermöglichen.\n",\
                     font='times 15', bg=bg_color)
splash_topic_desc.pack()

splash_guided_by_name = Label(splash_root, text="Guided by: Prof. Dipl.-Inf. Ingrid Scholl ", font='times 20', bg=bg_color)
splash_guided_by_name.pack(pady=10)

splash_team_names = Label(splash_root,justify="left", anchor="w", text=" Team: \n Florisa Zanier \t\t\t3613450 \n Sameer Tuteja \t\t\t3296444 \n Venkata Gopi Krishna Miriyala \t3601156", font='times 20 ', bg=bg_color)
splash_team_names.pack()

B = Button(splash_root, text ="Continue to app", command = splash_root.destroy)
B.pack(pady=10)

splash_root.after(20000,splash_root.destroy) #after(ms,func)
splash_root.protocol('WM_DELETE_WINDOW', exitFunction) 
splash_root.mainloop()

# Tkinter setup
root = Tk()
root.title("Air Canvas")
frm = ttk.Frame(root, padding=10)
frm.grid()

label_var = "Use Index finger to draw \nGesture Recognition Results"


canvas = Canvas(frm, width=640, height=480)
canvas.grid(column=0, row=3, columnspan=2)
# result_label = ttk.Label(frm, textvariable=label_var)
# result_label.grid(column=0, row=0, columnspan=2)

# Create labels to display frames
tracking_label = Label(root, height=450)  # Adjust the height value as needed
tracking_label.grid(row=0, column=0, padx=10, pady=5)

paint_label = Label(root)
paint_label.grid(row=0, column=1, padx=10, pady=5)  # Use grid method

paint_label_panel = Label(root)
paint_label_panel.grid(row=1, column=0, padx=10, pady=5)  # Use grid method

right_bottom_pannel = Frame(root)
right_bottom_pannel.grid(row=1, column=1, padx=10, pady=5)  # Use grid method

label_panel = Label(right_bottom_pannel, text=label_var)
label_panel.grid(row=0, column=0, padx=10, pady=5)  # Use grid method

save_image_panel = Button(right_bottom_pannel, text="Save image", command=image_save_called)
save_image_panel.grid(row=1, column=0, padx=10, pady=5)  # Use grid method

exit_panel = Button(right_bottom_pannel, text="Exit", command=exitFunction)
exit_panel.grid(row=1, column=1, padx=10, pady=5)  # Use grid method

def start_camera():
    # Keep looping
    prev_gesture_label = -1
    global paintWindow

    # Initialize colorIndex before the while loop
    global colorIndex
    colorIndex = 0
    while True:
        # Reading the frame from the camera
        ret, frame = cap.read()

        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                # Classify the gesture based on the angle
                gesture_label = classify_gesture(hand_landmarks)

                # Display the recognized gesture label
                # gesture_result = f"Use Index finger to draw \nDetected Gesture: {gesture_labels[gesture_label]},Selected Colors: {colors_strings[colorIndex]}",
                gesture_result = "Use Index finger to draw \nDetected Gesture: "+str(gesture_labels[gesture_label])+"\n Selected Color: "+str(colors_strings[colorIndex]),
                update_label(gesture_result)
                
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Check for color assignment gestures
                if gesture_label in [1, 2, 4, 5, 6]:
                # Update the color index based on the detected gesture
                    if gesture_label == 1:  # Closed_Fist
                        colorIndex = 3  # Yellow
                    elif gesture_label == 2:  # Open_Palm

                        # Clear
                        bpoints[blue_index].clear()
                        gpoints[green_index].clear()
                        rpoints[red_index].clear()
                        ypoints[yellow_index].clear()

                        # Clear lines in paintWindow
                        paintWindow = np.zeros((471, 636, 3)) + 255
                        paintWindow = cv2.flip(paintWindow, 1)
                        
                    elif gesture_label == 4:  # Thumb_Down
                        colorIndex = 2  # Red
                    elif gesture_label == 5:  # Thumb_Up
                        colorIndex = 1  # Green
                    elif gesture_label == 6:  # Victory
                        colorIndex = 0

                    if gesture_label != prev_gesture_label:
                        if gesture_label != 0 and gesture_label != 2 and gesture_label != 3 :  # Check if the gesture is not unknown
                        # Call the speech function for all gestures except unknown
                            speak_gesture(gesture_label)   


                    bpoints[blue_index].clear()
                    gpoints[green_index].clear()
                    rpoints[red_index].clear()
                    ypoints[yellow_index].clear()


                    # Update the previous gesture label
                    prev_gesture_label = gesture_label

                if gesture_label == 3 and prev_gesture_label in [1, 2, 4, 5, 6]:  # Pointing_Up
                    tip_of_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Update the corresponding color points list
                    if colorIndex == 0:
                        bpoints[blue_index].appendleft((int(tip_of_finger.x * frame.shape[1]), int(tip_of_finger.y * frame.shape[0])))
                    elif colorIndex == 1:
                        gpoints[green_index].appendleft((int(tip_of_finger.x * frame.shape[1]), int(tip_of_finger.y * frame.shape[0])))
                    elif colorIndex == 2:
                        rpoints[red_index].appendleft((int(tip_of_finger.x * frame.shape[1]), int(tip_of_finger.y * frame.shape[0])))
                    elif colorIndex == 3:
                        ypoints[yellow_index].appendleft((int(tip_of_finger.x * frame.shape[1]), int(tip_of_finger.y * frame.shape[0])))


                    center = (int(tip_of_finger.x * frame.shape[1]), int(tip_of_finger.y * frame.shape[0]))

                # Draw an enclosing circle around the tip of the index finger
                    circle_radius = int(frame.shape[0] * 0.1)  # 60% of the frame height
                    cv2.circle(frame, center, circle_radius, (0, 255, 0), 2)  # Example: Drawing an enclosing circle

                # Draw lines of all the colors on the canvas and frame
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)


                # Convert frames to Tkinter format
        tracking_image = convert_to_tkinter(frame, flip=True)
        paint_image = convert_to_tkinter(paintWindow, flip=True)
        paint_image_panel = convert_to_tkinter(paintWindow_panel)

                # Update labels with new images
        tracking_label.config(image=tracking_image)
        tracking_label.image = tracking_image

        paint_label.config(image=paint_image)
        paint_label.image = paint_image

        paint_label_panel.config(image=paint_image_panel)
        paint_label_panel.image = paint_image_panel

        if image_saved:
            save_image(paintWindow)

        # Update Tkinter window
        root.update()

        #quit_button = Button(frm, text="Quit", command=root.destroy)
        #quit_button.grid(column=1, row=1, sticky=E)        

# Start the camera in a separate thread
camera_thread = threading.Thread(target=start_camera)
camera_thread.start()

root.protocol('WM_DELETE_WINDOW', exitFunction) 

# Start the Tkinter main loop
root.mainloop()