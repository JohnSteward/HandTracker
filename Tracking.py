import cv2
import numpy as np
import mediapipe as mp

# Set up the hand tracker
handSol = mp.solutions.hands
hands = handSol.Hands(model_complexity=0, min_detection_confidence=0.4, max_num_hands=1, min_tracking_confidence=0.4)

# Capture video from camera (0 is the default)
videoCapture = cv2.VideoCapture(1)
videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
while True:
    success, img = videoCapture.read()
    if success:
        img = cv2.flip(img, 1)
        recHands = hands.process(img)
        prevPos = []
        if recHands.multi_hand_landmarks:
            # Recognising one hand and storing its position so we can see how far it has moved
            for hand in recHands.multi_hand_landmarks:
                for datapointID, point in enumerate(hand.landmark):
                    h, w, c = img.shape
                    x, y = int(point.x * w), int(point.y * h)
                    cv2.circle(img, (x,y), 10, (255, 0, 255), cv2.FILLED)
                prevPos = [point for point in hand.landmark]
    cv2.imshow("Cam Output", img)
    cv2.waitKey(5)