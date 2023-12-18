import cv2
import mediapipe as mp
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import math

model_path = 'C:\\Users\\gpmk9\\OneDrive\\Desktop\\M.Sc Mechatronics\\SEM 3\\3d Buidverarbeitung\\Project\\gesture_recognizer.task'

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

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
    7: "ILoveYou"
}

# Use OpenCV’s VideoCapture to start capturing from the webcam.
cap = cv2.VideoCapture(0)

def update_label(result_text):
    label_var.set(result_text)

def calculate_angle(point1, point2):
    angle_rad = math.atan2(point2.y - point1.y, point2.x - point1.x)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def classify_gesture(angle):
    # Adjust these thresholds based on your specific angles
    if 0 <= angle <= 45:
        return 3  # Pointing_Up
    elif 45 < angle <= 135:
        return 1  # Closed_Fist
    elif -45 > angle >= -135:
        return 2  # Open_Palm
    elif angle > 135:
        return 5  # Thumb_Up
    elif angle < -135:
        return 4  # Thumb_Down
    else:
        return 0  # Unknown

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()

label_var = StringVar()
label_var.set("Gesture Recognition Results")
result_label = ttk.Label(frm, textvariable=label_var)
result_label.grid(column=0, row=0, columnspan=2)

canvas = Canvas(frm, width=640, height=480)
canvas.grid(column=0, row=1, columnspan=2)

ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Perform gesture recognition based on hand landmarks
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate angle between thumb and index finger
            angle = calculate_angle(thumb_tip, index_finger)

            # Classify the gesture based on the angle
            gesture_label = classify_gesture(angle)

            # Display the recognized gesture label
            gesture_result = f"Detected Gesture: {gesture_labels[gesture_label]}"
            update_label(gesture_result)

        # Draw landmarks on the frame
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Convert the OpenCV frame to a Tkinter-compatible PhotoImage
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    img = ImageTk.PhotoImage(image=img)

    # Display the frame in the Tkinter applet
    canvas.config(width=img.width(), height=img.height())
    canvas.img = img
    canvas.create_image(0, 0, anchor=NW, image=img)

    # Allow GUI to update
    root.update_idletasks()
    root.update()

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()

root.mainloop()
