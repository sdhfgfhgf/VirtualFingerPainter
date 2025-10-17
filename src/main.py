import cv2
import numpy as np
import mediapipe as mp

source = 0
cap = cv2.VideoCapture(source)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

def fingers_up(handLms):
    fingers = []
    if label == "Right":
        fingers.append(1 if handLms.landmark[4].x < handLms.landmark[3].x else 0)
    else:  # Left hand
        fingers.append(1 if handLms.landmark[4].x > handLms.landmark[3].x else 0)

    tips = [8, 12, 16, 20]
    joints = [6, 10, 14, 18]

    for tip, joint in zip(tips, joints):
        if handLms.landmark[tip].y < handLms.landmark[joint].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

prev_x, prev_y = None, None
canvas = None

while (True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if canvas is None:
        h, w, c = frame.shape
        canvas = np.zeros((int(h), int(w), 3), np.uint8)

    if results.multi_hand_landmarks:
        for handLms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            if label == 'Right':
                fingers = fingers_up(handLms)

                if fingers == [0, 1, 0, 0, 0]:
                    lm = handLms.landmark[8]
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    if prev_x is None:
                        prev_x, prev_y = cx, cy

                    cv2.line(canvas, (prev_x, prev_y), (cx, cy), (255, 0, 255), 5)
                    prev_x, prev_y = cx, cy

                elif fingers == [1, 1, 1, 1, 1]:
                    prev_x, prev_y = None, None

                else:
                    prev_x, prev_y = None, None
            elif label == 'Left':
                fingers = fingers_up(handLms)
                if fingers == [1, 1, 1, 1, 1]:
                    canvas = np.zeros((h, w, 3), np.uint8)
                    prev_x, prev_y = None, None

            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
    output = cv2.addWeighted(canvas, 0.5, frame, 0.5, 0, frame)
    cv2.imshow('webcamFeed', output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

