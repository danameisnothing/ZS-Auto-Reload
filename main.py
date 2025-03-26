# Code plagiarised from : https://stackoverflow.com/questions/27117705/how-to-update-imshow-window-for-python-opencv-cv2, https://github.com/bar-ji/OpenCV-Minecraft-Diamond-Bot/blob/main/Minecraft%20Auto%20Miner/Miner.py
# This only works if you're on windowed mode, sorry

import time
import pyautogui
import cv2
import numpy as np
import keyboard
import dxcam
import pytesseract
from concurrent import futures
import Levenshtein
import signal

# Constants
LOWER_RANGE_AMMO_VIS: np.ndarray = np.array([0, 0, 254])
UPPER_RANGE_AMMO_VIS: np.ndarray = np.array([1, 1, 255])
UPPER_RANGE_TEXT_THRESHOLD: np.ndarray = np.array([1, 1, 255])
LOWER_RANGE_TEXT_THRESHOLD: np.ndarray = np.array([0, 0, 254])
LOW_PIXEL_COMPENSATE_DURATION: float = 0.02 # a lazy fix for the weapon reloading after taking damage (the screen turned red), Don't set this value too high, otherwise it may miss a reload
LOW_PIXEL_MAX_CONSECUTIVE_PRESS: int = 2
THRESHOLD_WEAPONS: dict = {
    "Bluesteel G18": 270,
    "Flush PPSh-41": 350,
    "Deagle .50": 100,
    "Ice Deagle .50": 100,
    "Ultimax 100": 70, # 63 or 126
    "Cotton Candy HK21": 130
}

def processScreenshot(img: np.ndarray, upper_threshold: np.ndarray, lower_threshold: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_threshold, upper_threshold)
    return mask

def tess(img: np.ndarray) -> str:
    res: str = pytesseract.image_to_string(img, config="--psm 7")
    return res.strip()

def captureSigint(sig, frame) -> None:
    screen.stop()
    cv2.destroyAllWindows()
    exit(0)

reloadDebounce: bool = False # false is not pressing, true is pressing
screenX: int = pyautogui.size().width
screenY: int = pyautogui.size().height
lastReloadTick: float = time.time()
consecutivePress: int = 0

screen: dxcam.DXCamera = dxcam.create()
screen.start(region=(1664, 925, 1901, 1058), target_fps=120) # 1398, 828 on 1600 * 900 | region=(1668, 1034, 1883, 1058) | region=(1668, 1034, 1693, 1058) | #-40 | 1668, 1034, 1883, 1058

#lastTime: float = time.perf_counter()

lastWeaponNameThread: None | futures.Future = None

lastWeaponName: str = ""

# The first press_and_release is called, the input is dropped?
keyboard.press_and_release("F24")

signal.signal(signal.SIGINT, captureSigint)
#lastAmmoCountThread: None | futures.Future = None

print("Started")
while True:
    img = screen.get_latest_frame()

    weaponNameImgPixel = processScreenshot(img[:20, :], UPPER_RANGE_TEXT_THRESHOLD, LOWER_RANGE_TEXT_THRESHOLD)
    ammoCountImgPixel = processScreenshot(img[40:96, :125], UPPER_RANGE_TEXT_THRESHOLD, LOWER_RANGE_TEXT_THRESHOLD)
    ammoVisImgPixel = processScreenshot(img[110:, 4:220], UPPER_RANGE_AMMO_VIS, LOWER_RANGE_AMMO_VIS) # processScreenshot(img[108:, 4:220], UPPER_RANGE_AMMO_VIS, LOWER_RANGE_AMMO_VIS) # img[108:, 4:220] (original, full section, changed because the ammo text animation when shooting, scrolls down to this range, that could interfere with detection)

    ammoVisPixelCount = cv2.countNonZero(ammoVisImgPixel)
    
    if lastWeaponNameThread is None:
        lastWeaponNameThread = futures.ThreadPoolExecutor().submit(tess, weaponNameImgPixel)
    elif lastWeaponNameThread.running():
        pass
    else:
        lastWeaponName = lastWeaponNameThread.result()
        lastWeaponNameThread = None
    
    """if lastAmmoCountThread is None:
        lastAmmoCountThread = futures.ThreadPoolExecutor().submit(tess, ammoCountImgPixel)
    elif lastAmmoCountThread.running():
        pass
    else:
        print(lastAmmoCountThread.result())
        lastAmmoCountThread = None"""
    
    """bulletTypePixel = cv2.countNonZero(processScreenshot(bulletType))

    if bulletTypePixel >= 150 and bulletTypePixel <= 160:
        lastBulletType = "RIFLE"
    elif bulletTypePixel >= 280 and bulletTypePixel <= 290:
        lastBulletType = "PISTOL"
    
    match lastBulletType:
        case "PISTOL":
            RELOAD_PIXEL_NUM_TRESHOLD = 500
        case "RIFLE":
            RELOAD_PIXEL_NUM_TRESHOLD = 600
        case _:
            RELOAD_PIXEL_NUM_TRESHOLD = 500"""

    """cv2.namedWindow("hsv_debug_weaponname", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv_debug_weaponname", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv_debug_weaponname", weaponNameImgPixel)

    cv2.namedWindow("hsv_debug_ammocount", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv_debug_ammocount", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv_debug_ammocount", ammoCountImgPixel)

    cv2.namedWindow("hsv_debug_ammovis", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv_debug_ammovis", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv_debug_ammovis", ammoVisImgPixel)

    cv2.namedWindow("hsv_debug_bullettype", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("hsv_debug_bullettype", cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow("hsv_debug_bullettype", bulletType)
    cv2.waitKey(5)"""

    #print(f"Ammo Pixel : {ammoVisPixelCount}")
    #print("Bullet Type Pixel : "+ str(bulletTypePixel) + ", BulletType : " + str(lastBulletType))
    for base_weapons in THRESHOLD_WEAPONS.keys():
        # Like this, because the skin name has more characters (e.g. "Galaxy G18".find("G18"))
        if Levenshtein.distance(lastWeaponName, base_weapons) <= 3:
            if int(ammoVisPixelCount) < THRESHOLD_WEAPONS.get(base_weapons) and int(ammoVisPixelCount) > 0:
                if not reloadDebounce and time.time() - lastReloadTick >= LOW_PIXEL_COMPENSATE_DURATION:
                    if consecutivePress <= LOW_PIXEL_COMPENSATE_DURATION:
                        keyboard.press_and_release("R")
                        reloadDebounce = True
                        consecutivePress += 1
                        print(f"Reloaded {base_weapons} with threshold {THRESHOLD_WEAPONS.get(base_weapons)}")
            else:
                lastReloadTick = time.time()
                reloadDebounce = False
                if consecutivePress - 1 >= 0:
                    consecutivePress -= 1
    
    """time.sleep(0.01)
    print(f"{1/(time.perf_counter() - lastTime)} fps")
    lastTime = time.perf_counter()"""