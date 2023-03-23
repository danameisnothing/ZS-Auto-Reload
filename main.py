# Code plagiarised from : https://stackoverflow.com/questions/27117705/how-to-update-imshow-window-for-python-opencv-cv2, https://github.com/bar-ji/OpenCV-Minecraft-Diamond-Bot/blob/main/Minecraft%20Auto%20Miner/Miner.py
# This only works if you're on windowed mode, sorry

import time
import os
import pyautogui
import cv2
import numpy as np
import keyboard
# import d3dshot i wanted it to but it's too complicated for normal users (you have to download the project from github, fix a file, and install it from there)

# Constants
TEMP_FOLDER = "TEMP"
TEMP_FULL_AMMO_FILE = "ammo.png"
LOWER_RANGE_AMMO_VIS = np.array([0, 0, 0])
# UPPER_RANGE_AMMO_VIS = np.array([25, 15, 255])
UPPER_RANGE_AMMO_VIS = np.array([179, 7, 255])
LOW_PIXEL_COMPENSATE_DURATION = 0.07 # a lazy fix for the weapon reloading after taking damage (the screen turned red), Don't set this value too high, otherwise it may miss a reload

def createFolder(dir):
    try:
        os.mkdir(dir)
    except OSError:
        assert True # bruh

def processScreenshot(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_RANGE_AMMO_VIS, UPPER_RANGE_AMMO_VIS)
    return mask

reloadDebounce = False # false is not pressing, true is pressing
screenX = pyautogui.size().width
screenY = pyautogui.size().height
lastReloadTick = time.time()

createFolder(TEMP_FOLDER)

while True:
    # can run at about 20 times a second
    pyautogui.screenshot(TEMP_FOLDER + "\\" + TEMP_FULL_AMMO_FILE, region=(screenX - 202, screenY - 72, 180, 16)) # 1398, 828 on 1600 * 900
    #rawImg = ImageGrab.grab(bbox=(screenX - 202, screenY - 72, (screenX - 202) + 180, (screenY - 72) + 16))
    
    ammoImg = cv2.imread(TEMP_FOLDER + "\\" + TEMP_FULL_AMMO_FILE, cv2.IMREAD_COLOR)
    ammoImgPixel = cv2.countNonZero(processScreenshot(ammoImg))

    cv2.namedWindow("hsv", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv", processScreenshot(ammoImg))
    cv2.waitKey(1)

    print("Ammo Pixel : " + str(ammoImgPixel))
    # Reloading on 2 ammo left on a rifle bullet icon thing
    # 590
    # Need to be higher to compensate for 1 bullet loss
    # Higher than 1 to prevent reloading because this thing is so slow
    if int(ammoImgPixel) < 240 and int(ammoImgPixel) > 0:
        if not reloadDebounce and time.time() - lastReloadTick >= LOW_PIXEL_COMPENSATE_DURATION:
            keyboard.press_and_release("R")
            reloadDebounce = True
    else:
        lastReloadTick = time.time()
        reloadDebounce = False
    
