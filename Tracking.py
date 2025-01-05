import cv2
import numpy as np
import mediapipe as mp
import pyautogui as keyPress
import keyboard
import math


class Hands:
    def __init__(self, up, down, left, right):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        # Capture video from camera (0 is the default)
        self.videoCapture = cv2.VideoCapture(0)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.handSol = mp.solutions.hands
        self.detectCon = 0.7
        self.trackCon = 0.7
        self.hands = self.handSol.Hands(model_complexity=1, min_detection_confidence=self.detectCon, max_num_hands=1,
                              min_tracking_confidence=self.trackCon)
        self.prevPos = []

    # Here we check whether it is the left or right hand being tracked, so we can have different inputs for each
    # Return 0 for left hand, 1 for right hand
    def WhichHand(self):
        pass

    # Here we check whether the user's hand is clenched and therefore do not want to input a gesture
    # We will check the distance between points on the hand and if they are small enough, the hand is clenched
    # (Will probably do distance between tip of index finger and palm)
    def IsTracking(self, hand, img):
        handPoints = hand.landmark
        fingerTip = handPoints[8]
        palm = handPoints[0]
        distance = math.sqrt(((fingerTip.x - palm.x)**2)+(fingerTip.y - palm.y)**2)
        if distance < 0.2:
            cv2.putText(img, "No Input", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                        cv2.LINE_4)
            return 0
        else:
            return 1


    # Here we do the main loop for tracking and recognising movements to send to the control scheme
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
                                if self.IsTracking(hand, img):
                                    if self.prevPos != []:

                                        # Checking if there has been a big movement, using the fact that it cannot pick up big
                                        # movements to my advantage, by using the previous position

                                        # Later, include more options, maybe do head movements as well/try to implement a CNN like
                                        # my initial idea, include left and right hand, this will be better for the gesture control scheme
                                        if float(point.x) > float(self.prevPos[0]) + 0.1:
                                            cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                        cv2.LINE_4)
                                            print('right')
                                            self.ControlScheme('right')
                                        if float(point.x) < float(self.prevPos[0]) - 0.1:
                                            cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                        cv2.LINE_4)
                                            self.ControlScheme('left')
                                            print('left')
                                        if float(point.y) < float(self.prevPos[1]) - 0.1:
                                            cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                        cv2.LINE_4)
                                            print('up')
                                            self.ControlScheme('up')
                                        if float(point.y) > float(self.prevPos[1]) + 0.1:
                                            cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                        cv2.LINE_4)
                                            print('down')
                                            self.ControlScheme('down')
                                    self.prevPos = [point.x, point.y]
                                else:
                                    # Resetting so it does not register an input when the fist is unclenched
                                    self. prevPos = []
            cv2.imshow("Cam Output", img)
            cv2.waitKey(5)

    # Here we can customise our control scheme based on the registered input (maybe make a gui for this later,
    # probably using TKinter, but maybe look up something else)
    def ControlScheme(self, inp):
        if inp == 'up':
            if not self.down:
                keyPress.keyDown('w')
                self.up = True
            else:
                keyPress.keyUp('s')
                self.down = False
        elif inp == 'down':
            if not self.up:
                keyPress.keyDown('s')
                self.down = True
            else:
                keyPress.keyUp('w')
                self.up = False
        elif inp == 'left':
            if not self.right:
                keyPress.keyDown('a')
                self.left = True
            else:
                keyPress.keyUp('d')
                self.right = False
        elif inp == 'right':
            if not self.left:
                keyPress.keyDown('d')
                self.right = True
            else:
                keyPress.keyUp('a')
                self.left = False



# Set up the hand tracker
handTracker = Hands(False, False, False, False)
handTracker.Tracking()