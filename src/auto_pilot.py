import RPi.GPIO as GPIO
from pynput.keyboard import Key, KeyCode, Listener
import time
import os
import numpy as np

from gpio_mgmt import GpioMgmt
from motor import Motor
from camera import Camera
from infrared import Infrared
from ultrasonic import Ultrasonic
from headlight import HeadLight
from settings import logging


# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
# 忽略警告信息
GPIO.setwarnings(False)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class AutoPilot(object):
    def __init__(self):
        self.init_motor()
        self.init_camera()
        # self.init_infrared()
        # self.init_ultrasonic()
        self.init_headlight()
        self.sens = DotDict({})

    def init_motor(self):
        self.motor = Motor()

    def init_camera(self):
        self.camera = Camera()

    def init_infrared(self):
        self.infrared = Infrared()

    def init_headlight(self):
        self.headlight = HeadLight()

    def init_ultrasonic(self):
        self.ultrasonic = Ultrasonic()

    def _pilot(self, deviation):
        if -5 <= deviation <= 5:
            self.motor.run(0.1, 65, 65)
        elif -5 < deviation <= -10:
           self.motor.left_run(0.08, left_speed=50, right_speed=60)
        elif -20 <= deviation < -10:
            self.motor.left_run(0.06, left_speed=30, right_speed=60)
        elif deviation < -20:
            self.motor.left_run(0.04, left_speed=20, right_speed=60)
        elif 5 < deviation <= 10:
           self.motor.right_run(0.1, left_speed=60, right_speed=50)
        elif 10 < deviation <= 20:
            self.motor.right_run(0.06, left_speed=60, right_speed=30)
        elif 20 < deviation:
            self.motor.right_run(0.04, left_speed=60, right_speed=20)
        self.motor.free()

    def _run(self):
        debug = 0
        counter = 0
        dev_cache = []
        while self.camera.cap.isOpened():

            counter += 1;
            try:
                deviation = self.camera.analyze()
                # logging.debug(f'deviation: {deviation}')
                # self._pilot(deviation)

                dev_cache.append(deviation)
                if counter >= 3:
                    avg_deviation = (sum(dev_cache) - max(dev_cache) - min(dev_cache))/ 3
                    logging.debug(f'avg_deviation: {avg_deviation}')
                    self._pilot(avg_deviation)
                    counter = 0
                    dev_cache = []
            except KeyboardInterrupt as e:
                time.sleep(5)
                counter = 0
                dev_cache = []
                continue

    def run(self):
        try:
            logging.debug('Start smartcar in mode auto_pilot with camera ...')
            GpioMgmt().init_pwm()
            # self.ultrasonic.init_pwm()
            self._run()
        #except KeyboardInterrupt as e:
        #    GpioMgmt().release()
        #    logging.info("[+] Exiting")
        #    raise e
        except Exception as e:
            GpioMgmt().init_pin()
            logging.error(str(e))


if __name__ == "__main__":
    ap = AutoPilot()
    ap.run()
