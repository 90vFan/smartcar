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


class StopCarException(Exception):
    """Stop car for debuggings""" 


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
        t = 0.1
        if -5 <= deviation <= 5:
            self.motor.run(t, 20, 20)
        elif -10 <= deviation < -5:
           self.motor.left_run(t, left_speed=15, right_speed=20)
        elif -20 <= deviation < -10:
            self.motor.left_run(t, left_speed=5, right_speed=20)
        elif deviation < -20:
            self.motor.left_run(t, left_speed=1, right_speed=20)
        elif 5 < deviation <= 10:
           self.motor.right_run(t, left_speed=20, right_speed=15)
        elif 10 < deviation <= 20:
            self.motor.right_run(t, left_speed=20, right_speed=5)
        elif 20 < deviation:
            self.motor.right_run(t, left_speed=20, right_speed=1)
        self.motor.free()
        #time.sleep(0.1)

    def _run(self):
        debug = 0
        counter = 0
        dev_cache = []
        momentum = 0
        dev_m = 0
        cache_len = 0

        while self.camera.cap.isOpened():
            counter += 1
            try:
                start = time.time()
                deviation = self.camera.analyze()
                # logging.debug(f'deviation: {deviation}')
                # self._pilot(deviation)
                if len(dev_cache) == 0:
                    avg_deviation = deviation
                if abs(deviation - avg_deviation) < 20:
                    dev_cache.append(deviation)

                if len(dev_cache) >= 3:
                    counter = 0
                    end = time.time()
                    delta = end - start
                    logging.debug(f'analyze 3 times: {delta:.3f}s')

                    avg_deviation = sum(dev_cache) / len(dev_cache)
                    dev_m = (0.3*dev_m + avg_deviation) / 1.3
                    logging.info(f'deviation momentum: {dev_m}')
                    self._pilot(dev_m)
            except KeyboardInterrupt as e:
                counter = 0
                dev_cache = []
                time.sleep(20)
                break

    def run(self):
        try:
            logging.debug('Start smartcar in mode auto_pilot with camera ...')
            GpioMgmt().init_pwm()
            # self.ultrasonic.init_pwm()
            self._run()
        except KeyboardInterrupt as e:
           GpioMgmt().release()
           logging.info("[+] Exiting")
           raise e
        except Exception as e:
            GpioMgmt().init_pin()
            logging.error(str(e))


if __name__ == "__main__":
    ap = AutoPilot()
    ap.run()
