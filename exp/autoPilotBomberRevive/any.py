from utilref import *

import random
import pyautogui
import cv2 as cv


class PID:

    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0
        self.integral = 0

    def update(self, error):
        derivative = error - self.last_error
        self.integral += error
        self.last_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative


def shot_match(name):
    template = cv.imread(name)
    screenshot = pyautogui.screenshot()
    # matchtemplate on the screenshot
    objects = cv.matchTemplate(screenshot, template)


def lockBase():

    bases = shot_match('baseOnMap.png')
    # pick one object randomly
    object_to_pick = random.choice(bases)

    # use pid on mouse moving left or right to control player orientation matches the direction from player to object
    pid = PID(1, 0, 0)
    while True:
        # hold M key to view map
        pyautogui.keyDown('M')

        # find the arrow indicating player, get the orientation facing
        player_arrow = shot_match('playerArrow.png')
        player_orientation = 0

        pyautogui.keyUp('M')

        # calculate the direction from player to object
        # convert object_to_pick and player_arrow to polar coordinates
        def cartesian_to_polar(coord):
            x, y = coord
            rho = np.sqrt(x**2 + y**2)
            phi = np.arctan2(y, x)
            return (rho, phi)

        object_to_pick_polar = cartesian_to_polar(object_to_pick -
                                                  player_arrow)

        # get the angle theta of object_to_pick in polar coordinates
        theta = object_to_pick_polar[1]

        # move the mouse left or right based on the pid output
        pid_output = pid.update(theta - player_orientation)
        if abs(pid_output) < 0.1:
            return
        pyautogui.move(pid_output, 0)


def getClimbRateNow():
    pass


def setClimbRate(climbrate):
    pid = PID(1, 0, 0)
    while True:
        climb_rate_now = getClimbRateNow()
        error = climbrate - climb_rate_now
        pid_output = pid.update(error)
        if abs(pid_output) < 0.1:
            return
        pyautogui.move(0, -pid_output)
