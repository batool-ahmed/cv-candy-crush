#tutorial: https://www.youtube.com/watch?v=jzXZVFqEE2I&list=WL

import cv2, cvzone, numpy as np, mediapipe
from cvzone.HandTrackingModule import HandDetector
from time import sleep
from pynput import keyboard
from pynput.keyboard import Controller, Key

cameraPort = 0
cap = cv2.VideoCapture(cameraPort, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=2)

keys = [ ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "b"] ]

finalText = ""

keyboard = Controller()

def drawAll(img, btnList):
    for btn in btnList:
        x, y = btn.pos
        w, h = btn.size
        cv2.rectangle(img, btn.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cvzone.cornerRect(img, (x, y, w, h), 28, rt=0)
        cv2.putText(img, btn.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    return img

def drawAllTransparent(img, btnList):
    imgNew = np.zeros_like(img, np.uint8)
    
    for btn in btnList:
        x, y = btn.pos
        w, h = btn.size
        cv2.rectangle(imgNew, btn.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(imgNew, btn.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    out = img.copy()
    alpha = 0.15
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]

    return out

class Button():
    def __init__(self, pos, text, size = [80, 80]) -> None:
        self.pos = pos
        self.size = size
        self.text = text
        x, y = self.pos
        w, h = self.size
        '''
        cv2.rectangle(img, self.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        '''
    '''
    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, self.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

        return img
    '''


#myButton = Button([100, 100], "Q")
buttonList = []

for i in range(0, len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

while True:
    success, img = cap.read()
    img = cv2.flip(img,1) #since webcam displays mirror image

    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)

    #img = myButton.draw(img)

    img = drawAll(img, buttonList)
    #img = drawAllTransparent(img, buttonList)

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            #according to mediapipe manual:
            #index 8 =  index finger tip 
            #index 12 = middle finger tip

            #lmList[finger][0 = x, 1 = y]

            #if distance between 8 and 12 is very small then it is a click
            if (x < lmList[8][0] < x + w) and (y < lmList[8][1] < y + w):
                #hovering over
                cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                length, _, _ = detector.findDistance(8, 12, img, draw=False)

                #clicking
                if length < 35:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    addText = True
                    #preventing repeating letters, veryyy lazy technique, sahi karo ye ajeeb
                    if button.text == "b":
                        if len(finalText) > 0:
                            finalText = finalText[:-1]
                            keyboard.press(Key.backspace)
                            keyboard.release(Key.backspace)
                    else:
                        #finalText += button.text
                        if len(finalText) > 0: 
                            if finalText[-1] == button.text:
                                addText = False
                        if addText:
                            finalText += button.text
                            keyboard.press(button.text)
                            keyboard.release(button.text)
                        
                    #sleep(0.05) #a lazy way of preventing multiple printing of one letter :(

    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    #cv2.rectangle(img, (750, 350), (880, 450), (175, 100, 175), cv2.FILLED)
    #cv2.putText(img, "BK", (770, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)


#cv2.destroyAllWindows()
