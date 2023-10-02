# import time
# import gameinput
# import pyautogui

# while True:
#     gameinput.press(gameinput.keycode.key_Enter, 0.01)
#     # pyautogui.keyDown("enter")
#     # time.sleep(0.05)
#     # pyautogui.keyUp("enter")
#     time.sleep(0.3)


import utilitypack

afi = utilitypack.AllFileIn(r"C:\CloudMusic")
afi = [
    f
    for f in afi
    if ((extpos := str.rfind(f, ".")) != -1 and f[extpos + 1 :] in ["mp3", "flac"])
]
[print(f) for f in afi]
