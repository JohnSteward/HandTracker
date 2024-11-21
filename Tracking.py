import cv2
import numpy as np
import mediapipe as mp

# Set up the hand tracker
handSol = mp.solutions.hands
hands = handSol.Hands(model_complexity=0, min_detection_confidence=0.4, max_num_hands=1, min_tracking_confidence=0.4)

# Capture video from camera (0 is the default)
videoCapture = cv2.VideoCapture(0)
videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
frame = 0
prevPos = []
while True:
    success, img = videoCapture.read()
    if success:
        img = cv2.flip(img, 1)
        recHands = hands.process(img)
        if recHands.multi_hand_landmarks:
            # Recognising one hand and storing its position so we can see how far it has moved
            for hand in recHands.multi_hand_landmarks:
                for datapointID, point in enumerate(hand.landmark):
                    h, w, c = img.shape
                    x, y = int(point.x * w), int(point.y * h)
                    cv2.circle(img, (x,y), 10, (255, 0, 255), cv2.FILLED)
                    if datapointID == 0:
                        # cv2.putText(img, str(point.y), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_4)
                        if prevPos != []:
                            # Checking if there has been a big movement, using the fact that it cannot pick up big
                            # movements to my advantage, by using the previous position

                            if float(point.x) > float(prevPos[0]) + 0.1:
                                cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_4)
                            if float(point.x) < float(prevPos[0]) - 0.1:
                                cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,cv2.LINE_4)
                            if float(point.y) < float(prevPos[1]) - 0.1:
                                cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                            if float(point.y) > float(prevPos[1]) + 0.1:
                                cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                        prevPos = [point.x, point.y]
                        #cv2.putText(img, str(point.x), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
    cv2.imshow("Cam Output", img)
    cv2.waitKey(5)