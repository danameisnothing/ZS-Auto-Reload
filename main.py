# Code plagiarised from : https://stackoverflow.com/questions/27117705/how-to-update-imshow-window-for-python-opencv-cv2, https://github.com/bar-ji/OpenCV-Minecraft-Diamond-Bot/blob/main/Minecraft%20Auto%20Miner/Miner.py
# This only works if you're on windowed mode, sorry

import time
import pyautogui
import cv2
import numpy as np
import keyboard
import dxcam

# Constants
LOWER_RANGE_AMMO_VIS = np.array([0, 0, 0])
# UPPER_RANGE_AMMO_VIS = np.array([25, 15, 255])
UPPER_RANGE_AMMO_VIS = np.array([179, 7, 255])
LOW_PIXEL_COMPENSATE_DURATION = 0.07 # a lazy fix for the weapon reloading after taking damage (the screen turned red), Don't set this value too high, otherwise it may miss a reload
RELOAD_PIXEL_NUM_TRESHOLD = 240

def processScreenshot(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_RANGE_AMMO_VIS, UPPER_RANGE_AMMO_VIS)
    return mask

reloadDebounce = False # false is not pressing, true is pressing
screenX = pyautogui.size().width
screenY = pyautogui.size().height
lastReloadTick = time.time()
screen = dxcam.create()
screen.start(region=(screenX - 202, screenY - 72, (screenX - 202) + 180, (screenY - 72)+ 16), target_fps=60) # 1398, 828 on 1600 * 900

while True:
    # now it has a dt of 0.03
    ammoImg = screen.get_latest_frame()
    ammoImgPixel = cv2.countNonZero(processScreenshot(ammoImg))

    cv2.namedWindow("hsv_debug", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv_debug", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv_debug", processScreenshot(ammoImg))
    cv2.waitKey(1)

    print("Ammo Pixel : " + str(ammoImgPixel))
    if int(ammoImgPixel) < RELOAD_PIXEL_NUM_TRESHOLD and int(ammoImgPixel) > 0:
        if not reloadDebounce and time.time() - lastReloadTick >= LOW_PIXEL_COMPENSATE_DURATION:
            keyboard.press_and_release("R")
            reloadDebounce = True
    else:
        lastReloadTick = time.time()
        reloadDebounce = False
    
