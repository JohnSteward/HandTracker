import cv2
import numpy as np
import mediapipe as mp
import pyautogui as keyPress
import keyboard

# Here we can customise our control scheme based on the registered input (maybe make a gui for this later)

class Hands:
    def __init__(self, up, down, left, right):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.videoCapture = cv2.VideoCapture(0)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.handSol = mp.solutions.hands
        self.hands = self.handSol.Hands(model_complexity=0, min_detection_confidence=0.4, max_num_hands=1,
                              min_tracking_confidence=0.4)
        self.prevPos = []


    def Tracking(self):
        while True:
            success, img = self.videoCapture.read()
            if success:
                img = cv2.flip(img, 1)
                recHands = self.hands.process(img)
                if recHands.multi_hand_landmarks:
                    # Recognising one hand and storing its position, so we can see how far it has moved
                    for hand in recHands.multi_hand_landmarks:
                        for datapointID, point in enumerate(hand.landmark):
                            h, w, c = img.shape
                            x, y = int(point.x * w), int(point.y * h)
                            cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                            if datapointID == 0:
                                if self.prevPos != []:

                                    # Checking if there has been a big movement, using the fact that it cannot pick up big
                                    # movements to my advantage, by using the previous position

                                    # Later, include more options, maybe do head movements as well/try to implement a CNN like
                                    # my initial idea, include left and right hand, this will be better for the gesture control scheme
                                    if float(point.x) > float(self.prevPos[0]) + 0.1:
                                        cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                    cv2.LINE_4)
                                        print('right')
                                    if float(point.x) < float(self.prevPos[0]) - 0.1:
                                        cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                    cv2.LINE_4)
                                        print('left')
                                    if float(point.y) < float(self.prevPos[1]) - 0.1:
                                        cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                        print('up')
                                        self.ControlScheme('up')
                                    if float(point.y) > float(self.prevPos[1]) + 0.1:
                                        cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                    cv2.LINE_4)
                                        print('down')
                                        self.ControlScheme('down')
                                        down = True
                                self.prevPos = [point.x, point.y]
                                # cv2.putText(img, str(point.x), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
            cv2.imshow("Cam Output", img)
            cv2.waitKey(5)


    def ControlScheme(self, input):
        if input == 'up':
            if not self.down:
                keyPress.keyDown('w')
                print('going up')
                self.up = True
            else:
                keyPress.keyUp('s')
                print('stop up')
                self.down = False
        elif input == 'down':
            if not self.up:
                keyPress.keyDown('s')
                print('going down')
                self.down = True
            else:
                keyPress.keyUp('w')
                print('stop down')
                self.up = False



# Set up the hand tracker
handTracker = Hands(False, False, False, False)
handTracker.Tracking()
# Capture video from camera (0 is the default)

frame = 0