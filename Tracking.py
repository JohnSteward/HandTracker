import cv2
import numpy as np
import mediapipe as mp
import pyautogui as keyPress
import pydirectinput
import keyboard
import math
from tkinter import *
from tkinter import ttk

from google.protobuf.json_format import MessageToDict


class Hands:
    # In the initialisation I will make the UI to customise the control scheme (there is a default if you want to
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
        self.face = mp.solutions.face_detection
        self.detectCon = 0.92
        self.trackCon = 0.92
        # Same format as the controls, then the last one is for no input
        self.input = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.4]
        self.calibInp = np.zeros(len(self.input))
        self.calibVals = []
        self.calibrate = False
        self.controls = []
        self.oneHands = self.handSol.Hands(model_complexity=1, min_detection_confidence=self.detectCon, max_num_hands=1,
                              min_tracking_confidence=self.trackCon)
        self.twoHands = self.handSol.Hands(model_complexity=1, min_detection_confidence=self.detectCon, max_num_hands=2,
                                           min_tracking_confidence=self.trackCon)
        self.faceTrack = self.face.FaceDetection(model_selection=1, min_detection_confidence=self.detectCon)
        self.prevPos = [[0,0],[0,0]]
        self.CustomControls()
        self.root.mainloop()

    # Here we check whether the user's hand is clenched and therefore do not want to input a gesture
    # We will check the distance between points on the hand and if they are small enough, the hand is clenched
    # (Will probably do distance between tip of index finger and palm)
    # The 0.2 value has been chosen by intuition for default, but calibration allows you to change
    def IsTracking(self, hand, img):
        handPoints = hand.landmark
        fingerTip = handPoints[8]
        palm = handPoints[0]
        distance = math.sqrt(((fingerTip.x - palm.x)**2)+(fingerTip.y - palm.y)**2)
        if distance < (self.input[-1])/2:
            cv2.putText(img, "No Input", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                        cv2.LINE_4)
            return 0
        else:
            return 1
    # Tells the code that we want to calibrate
    def Calibrate(self, contList, dropBox):
        self.calibrate = True
        self.SetCustom(contList, dropBox)
    # Sets controls based on how you customised them
    def SetCustom(self, contList, dropBox):
        controlList = ['', 'a','d','k', 's','releaseS','stop','n']
        for i in range(len(contList)):
            self.controls.append(controlList[dropBox.index(contList[i].get())])
        self.root.destroy()
    # Sets default controls for those who don't want to customise
    def DefaultControls(self):
        self.controls = ['k', '', 'a', 'd', 'releaseS', 's', 'stop', 'n']
        print(self.controls)
        self.root.destroy()

    # Makes the menu for customising controls
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
        calib = Button(self.root, text="Set and Calibrate", width=15, command=lambda: self.Calibrate(contList, dropBox)).pack()
        setCont = Button(self.root, text="Set Custom", width=10, command=lambda: self.SetCustom(contList, dropBox)).pack()
        default = Button(self.root, text="Set Default", width=10, command=lambda: self.DefaultControls()).pack()


    # This does the calibration procedure
    def CalibTrack(self):
        valid = False
        for k in range(len(self.calibInp)):
            while True:
                success, img = self.videoCapture.read()
                # Here we calibrate our controls
                if success:
                    img = cv2.flip(img, 1)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    recHands = self.oneHands.process(img)
                    if recHands.multi_hand_landmarks:
                        # Recognising one hand and storing its position, so we can see how far it has moved
                        for handID, hand in enumerate(recHands.multi_hand_landmarks):
                            handed = recHands.multi_handedness[handID].classification[0].label
                            for datapointID, point in enumerate(hand.landmark):
                                h, w, c = img.shape
                                x, y = int(point.x * w), int(point.y * h)
                                cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                                if datapointID == 0:
                                    if self.IsTracking(hand, img):
                                        if self.prevPos != [[0,0], [0,0]]:
                                            if k == 0:
                                                cv2.putText(img, "Please input your right hand upwards", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.y) < float(self.prevPos[0][1]) - 0.1) and (handed == 'Right'):
                                                    self.calibVals.append(float(self.prevPos[0][1]) - float(point.y))
                                            elif k == 1:
                                                cv2.putText(img, "Please input your right hand downwards", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.y) > float(self.prevPos[0][1]) + 0.1) and (handed == 'Right'):
                                                    self.calibVals.append(float(point.y) - float(self.prevPos[0][1]))
                                            elif k == 2:
                                                cv2.putText(img, "Please input your right hand left", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.x) < float(self.prevPos[0][0]) - 0.1) and (handed == 'Right'):
                                                    self.calibVals.append(float(self.prevPos[0][0]) - float(point.x))
                                            elif k == 3:
                                                cv2.putText(img, "Please input your right hand right", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.x) > float(self.prevPos[0][0]) + 0.1) and (handed == 'Right'):
                                                    self.calibVals.append(float(point.x) - float(self.prevPos[0][0]))
                                            elif k == 4:
                                                cv2.putText(img, "Please input your left hand upwards", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.y) < float(self.prevPos[1][1]) - 0.1) and (handed == 'Left'):
                                                    self.calibVals.append(float(self.prevPos[1][1]) - float(point.y))
                                            elif k == 5:
                                                cv2.putText(img, "Please input your left hand downwards", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.y) > float(self.prevPos[1][1]) + 0.1) and (handed == 'Left'):
                                                    self.calibVals.append(float(float(point.y) - self.prevPos[1][1]))
                                            elif k == 6:
                                                cv2.putText(img, "Please input your left hand left", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.x) < float(self.prevPos[1][0]) - 0.1) and (handed == 'Left'):
                                                    self.calibVals.append(float(self.prevPos[1][0]) - float(point.x))
                                            elif k == 7:
                                                cv2.putText(img, "Please input your left hand right", (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if (float(point.x) > float(self.prevPos[1][0]) + 0.1) and (handed == 'Left'):
                                                    self.calibVals.append(float(point.x) - float(self.prevPos[1][0]))
                                            elif k == 8:
                                                cv2.putText(img,
                                                            "Hold your hand at the desired distance and press enter",
                                                            (50, 50),
                                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4)
                                                if keyboard.is_pressed('enter'):
                                                    fingerTip = hand.landmark[8]
                                                    palm = hand.landmark[0]
                                                    distance = math.sqrt(
                                                        ((fingerTip.x - palm.x) ** 2) + (fingerTip.y - palm.y) ** 2)
                                                    self.input[-1] = distance
                                                    valid = True
                                        if handed == 'Right':
                                            self.prevPos[0] = [point.x, point.y]
                                        elif handed == 'Left':
                                            self.prevPos[1] = [point.x, point.y]

                if len(self.calibVals) == 3:
                    average = 0
                    for j in self.calibVals:
                        average += j
                    self.input[k] = average/3
                    self.calibVals = []
                    break
                elif valid:
                    break
                cv2.imshow("Cam Output", img)
                cv2.waitKey(5)

        print(self.input)

    # Here we do the main loop for tracking and recognising movements to send to the control scheme
    # Check for face when the user has clenched their fist (FUTURE WORK), as they will not register an input with the hands,
    # can give us more options for more complex games
    def Tracking(self):
        if self.calibrate:
            self.CalibTrack()
            self.calibrate = False
        while True:
            success, img = self.videoCapture.read()
            if success:
                img = cv2.flip(img, 1)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                recHands = self.twoHands.process(img)
                if recHands.multi_hand_landmarks:
                    # Recognising each hand and storing its position, so we can see how far it has moved
                    for handID, hand in enumerate(recHands.multi_hand_landmarks):
                        handed = recHands.multi_handedness[handID].classification[0].label
                        for datapointID, point in enumerate(hand.landmark):
                            h, w, c = img.shape
                            x, y = int(point.x * w), int(point.y * h)
                            cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                            if datapointID == 0:
                                if self.IsTracking(hand, img):
                                    # Checking which hand is in view (left or right) to determine which controls to use
                                    if self.prevPos != [[0,0],[0,0]]:
                                        # Checking if there has been a big movement, using the fact that it cannot pick up big
                                        # movements to my advantage, by using the previous position
                                        # We also have a max cap for the distance from prevPos to avoid issues with handedness
                                        if handed == 'Right' and self.prevPos[0] != [0,0] and \
                                                (math.sqrt((self.prevPos[0][0] - point.x)**2 + (self.prevPos[0][1] - point.y)**2)) < 0.4:
                                            if float(point.x) > float(self.prevPos[0][0]) + self.input[3]:
                                                cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(3)
                                            elif float(point.x) < float(self.prevPos[0][0]) - self.input[2]:
                                                cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(2)
                                            elif float(point.y) < float(self.prevPos[0][1]) - self.input[0]:
                                                cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(0)
                                            elif float(point.y) > float(self.prevPos[0][1]) + self.input[1]:
                                                cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(1)

                                        elif handed == 'Left' and self.prevPos[1] != [0,0] and \
                                                (math.sqrt((self.prevPos[1][0] - point.x)**2 + (self.prevPos[1][1] - point.y)**2)) < 0.4:
                                            if float(point.x) > float(self.prevPos[1][0]) + self.input[7]:
                                                cv2.putText(img, "right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                            (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(7)
                                            elif float(point.x) < float(self.prevPos[1][0]) - self.input[6]:
                                                cv2.putText(img, "left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                            (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(6)
                                            elif float(point.y) < float(self.prevPos[1][1]) - self.input[4]:
                                                cv2.putText(img, "up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                                            2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(4)
                                            elif float(point.y) > float(self.prevPos[1][1]) + self.input[5]:
                                                cv2.putText(img, "down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                            (0, 0, 0), 2,
                                                            cv2.LINE_4)
                                                self.ControlScheme(5)
                                    if handed == 'Right':
                                        self.prevPos[0] = [point.x, point.y]
                                    elif handed == 'Left':
                                        self.prevPos[1] = [point.x, point.y]
                                else:
                                    # Resetting so it does not register an input when the fist is unclenched
                                    self.prevPos = [[0,0],[0,0]]
            cv2.imshow("Cam Output", img)
            cv2.waitKey(1)

    # This is the code to check which input was performed and register the correct key command

    def ControlScheme(self, input):
        if self.controls[input] == 'releaseS':
            pydirectinput.keyUp('s')
        elif self.controls[input] == 'stop':
            if self.left:
                pydirectinput.keyUp('a')
                self.left = False
            if self.right:
                pydirectinput.keyUp('d')
                self.right = False
        elif self.controls[input] == 'esc':
            pydirectinput.press('esc')
        elif self.controls[input] == 'k':
            pydirectinput.press('k')

        else:
            cont = self.controls[input]
            pydirectinput.keyDown(cont)
            if cont == 'a':
                self.left = True
                self.right = False
                pydirectinput.keyUp('d')
            elif cont == 'd':
                self.right = True
                self.left = False
                pydirectinput.keyUp('a')


# Set up the hand tracker
handTracker = Hands(False, False, False, False)
handTracker.Tracking()