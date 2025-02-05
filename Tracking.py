import cv2
import numpy as np
import mediapipe as mp
import pyautogui as keyPress
import keyboard
import math
from tkinter import *
from tkinter import ttk

from google.protobuf.json_format import MessageToDict


class Hands:
    # In the initialisation I will make the UI to customise the control scheme (there will be a default if you want to
    # skip it)
    def __init__(self, up, down, left, right):
        self.root = Tk()
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        # Capture video from camera (0 is the default)
        self.videoCapture = cv2.VideoCapture(0)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.handSol = mp.solutions.hands
        self.detectCon = 0.2
        self.trackCon = 0.6
        self.controls = []
        self.hands = self.handSol.Hands(model_complexity=1, min_detection_confidence=self.detectCon, max_num_hands=2,
                              min_tracking_confidence=self.trackCon)
        self.prevPos = [[],[]]
        self.CustomControls()
        self.root.mainloop()

    # Here we check whether the user's hand is clenched and therefore do not want to input a gesture
    # We will check the distance between points on the hand and if they are small enough, the hand is clenched
    # (Will probably do distance between tip of index finger and palm)
    # The 0.2 value has been chosen by intuition (realised this will change with distance from camera, maybe adjust
    # according to Z value)
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

    def SetCustom(self, contList, dropBox):
        controlList = ['', 'a','d','space','s','releaseS','stop','esc']
        for i in range(len(contList)):
            self.controls.append(controlList[dropBox.index(contList[i].get())])
        self.root.destroy()

    def DefaultControls(self):
        self.controls = ['space', '', 'a', 'd', 'releaseS', 's', 'stop', 'esc']
        print(self.controls)
        self.root.destroy()

    def CustomControls(self):
        self.root.title("Controls")
        dropBox = ['None', 'Left', 'Right', 'Jump', 'Crouch', 'Un-Crouch', 'Stop', 'Pause/Unpause']
        rightHand = Text(self.root, height=2, width=30)
        rightHand.pack()
        rightHand.insert(END, "Right Hand: ")
        Label(self.root, text="Up").pack()
        rightUp = ttk.Combobox(self.root, values=dropBox)
        rightUp.pack()
        Label(self.root, text="Down").pack()
        rightDown = ttk.Combobox(self.root, values=dropBox)
        rightDown.pack()
        Label(self.root, text="Left").pack()
        rightLeft = ttk.Combobox(self.root, values=dropBox)
        rightLeft.pack()
        Label(self.root, text="Right").pack()
        rightRight = ttk.Combobox(self.root, values=dropBox)
        rightRight.pack()

        leftHand= Text(self.root, height=2, width=30)
        leftHand.pack()
        leftHand.insert(END, "Left Hand: ")
        Label(self.root, text="Up").pack()
        leftUp = ttk.Combobox(self.root, values=dropBox)
        leftUp.pack()
        Label(self.root, text="Down").pack()
        leftDown = ttk.Combobox(self.root, values=dropBox)
        leftDown.pack()
        Label(self.root, text="Left").pack()
        leftLeft = ttk.Combobox(self.root, values=dropBox)
        leftLeft.pack()
        Label(self.root, text="Right").pack()
        leftRight = ttk.Combobox(self.root, values=dropBox)
        leftRight.pack()

        contList = [rightUp, rightDown, rightLeft, rightRight, leftUp, leftDown, leftLeft, leftRight]
        setCont = Button(self.root, text="Set Custom", width=10, command=lambda: self.SetCustom(contList, dropBox)).pack()
        default = Button(self.root, text="Set Default", width=10, command=lambda: self.DefaultControls()).pack()

    # Here we do the main loop for tracking and recognising movements to send to the control scheme
    # Check for face when a certain condition is met (like a gesture?), can give us more options for more complex games
    def Tracking(self):
        while True:
            success, img = self.videoCapture.read()
            if success:
                img = cv2.flip(img, 1)
                recHands = self.hands.process(img)
                # Works even when I twist my hand, idk why, research this
                if recHands.multi_hand_landmarks:
                    # Recognising one hand and storing its position, so we can see how far it has moved
                    for hand in recHands.multi_hand_landmarks:
                        handed = []
                        for i in recHands.multi_handedness:
                            handed.append(MessageToDict(i)['classification'][0]['label'])
                        for datapointID, point in enumerate(hand.landmark):
                            h, w, c = img.shape
                            x, y = int(point.x * w), int(point.y * h)
                            cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                            if datapointID == 0:
                                if self.IsTracking(hand, img):
                                    # Checking which hand is in view (left or right) to determine which controls to use

                                    if self.prevPos != [[],[]]:

                                        # Checking if there has been a big movement, using the fact that it cannot pick up big
                                        # movements to my advantage, by using the previous position
                                        for i in handed:
                                            if i == 'Right' and self.prevPos[0] != []:
                                                if float(point.x) > float(self.prevPos[0][0]) + 0.1:
                                                    cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    print('right')
                                                    self.ControlScheme(3)
                                                if float(point.x) < float(self.prevPos[0][0]) - 0.1:
                                                    cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    self.ControlScheme(2)
                                                    print('left')
                                                if float(point.y) < float(self.prevPos[0][1]) - 0.1:
                                                    cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    print('up')
                                                    self.ControlScheme(0)
                                                if float(point.y) > float(self.prevPos[0][1]) + 0.1:
                                                    cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    print('down')
                                                    self.ControlScheme(1)
                                                self.prevPos[0] = [point.x, point.y]
                                            elif i == 'Left' and self.prevPos[1] != []:
                                                if float(point.x) > float(self.prevPos[1][0]) + 0.1:
                                                    cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                                (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    print('right')
                                                    self.ControlScheme(7)
                                                if float(point.x) < float(self.prevPos[1][0]) - 0.1:
                                                    cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                                (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    self.ControlScheme(6)
                                                    print('left')
                                                if float(point.y) < float(self.prevPos[1][1]) - 0.1:
                                                    cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                                                2,
                                                                cv2.LINE_4)
                                                    print('up')
                                                    self.ControlScheme(4)
                                                if float(point.y) > float(self.prevPos[1][1]) + 0.1:
                                                    cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                                (0, 0, 0), 2,
                                                                cv2.LINE_4)
                                                    print('down')
                                                    self.ControlScheme(5)
                                                self.prevPos[1] = [point.x, point.y]
                                        if handed == 'Right':
                                            self.prevPos[0] = [point.x, point.y]
                                        elif handed == 'Left':
                                            self.prevPos[1] = [point.x, point.y]
                                else:
                                    # Resetting so it does not register an input when the fist is unclenched
                                    self.prevPos = [[],[]]
            cv2.imshow("Cam Output", img)
            cv2.waitKey(5)

    # Here we can customise our control scheme based on the registered input (maybe make a gui for this later,
    # probably using TKinter, but maybe look up something else)

    def ControlScheme(self, input):
        if self.controls[input] == 'releaseS':
            keyPress.keyUp('s')
            print('release')
        elif self.controls[input] == 'stop':
            if self.left:
                keyPress.keyUp('a')
                print('stop left')
                self.left = False
            if self.right:
                print('stop left')
                keyPress.keyUp('d')
                self.right = False
        elif self.controls[input] == 'esc':
            print('esc')
            keyPress.press('esc')
        else:
            cont = self.controls[input]
            print(cont)
            keyPress.keyDown(cont)
            if cont == 'a':
                self.left = True
            elif cont == 'd':
                self.right = True


# Set up the hand tracker
handTracker = Hands(False, False, False, False)
handTracker.Tracking()