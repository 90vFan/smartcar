import RPi.GPIO as GPIO
from pynput.keyboard import Key, KeyCode, Listener
import time
import os

from gpio_mgmt import GpioMgmt
from motor import Motor
from infrared import Infrared
from ultrasonic import Ultrasonic
from headlight import HeadLight
from settings import logging


# # 设置GPIO口为BCM编码方式
# GPIO.setmode(GPIO.BCM)
# # 忽略警告信息
# GPIO.setwarnings(False)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class AutoPilot(object):
    def __init__(self):
        self.init_motor()
        self.init_infrared()
        self.init_ultrasonic()
        self.init_headlight()
        self.sens = DotDict({})

    def init_motor(self):
        self.motor = Motor()

    def init_infrared(self):
        self.infrared = Infrared()

    def init_headlight(self):
        self.headlight = HeadLight()

    def init_ultrasonic(self):
        self.ultrasonic = Ultrasonic()

    def infrared_detect(self):
        left_sensor, right_sensor = self.infrared.detect()
        self.sens.infrared = DotDict({
            'left': left_sensor,
            'right': right_sensor
        })

    def ultrasonic_detect(self):
        front_distance, left_distance, right_distance = self.ultrasonic.detect()
        self.sens.distance = DotDict({
            'front': front_distance,
            'left': left_distance,
            'right': right_distance
        })

    def detect(self):
        self.ultrasonic_detect()
        self.infrared_detect()

    def _pilot(self):
        block = True
        self.detect()
        if self.sens.distance.front > 50:
            infrared_block = self.infrared_detect_to_turn_car()
            if not infrared_block:
                block = False
                self.motor.run(0.1)
                time.sleep((self.sens.distance.front - 50) / 500)
                logging.debug('Run forward   ^')
        elif 20 <= self.sens.distance.front <= 50:
            self.infrared_detect_to_turn_car()
        elif self.sens.distance.front < 20:
            self.turn_back()

        self.motor.free()
        return block

    def infrared_detect_to_turn_car(self):
        infrared_block = True
        if self.sens.infrared.left is True and self.sens.infrared.right is False:
            self.turn_right()
        elif self.sens.infrared.left is False and self.sens.infrared.right is True:
            self.turn_left()
        elif self.sens.infrared.left is False and self.sens.infrared.right is False:
            self.turn_back()
        else:
            infrared_block = False

        return infrared_block

    def _on_press(self, key):
        logging.debug(f'Press {key}')
        if key == Key.space:
            self.motor.brake()
        elif key == Key.ctrl:
            self._pilot()
        if key == Key.up:
            logging.debug('Run forward   ^')
            self.motor.run(0.1)
        elif key == Key.down:
            logging.debug('Run backward  _')
            self.motor.back(0.1)
        elif key == Key.left:
            logging.debug('Run left      <-')
            self.motor.left(0.1)
        elif key == Key.right:
            logging.debug('Run right     ->')
            self.motor.right(0.1)
        elif key == KeyCode(char='q'):
            logging.debug('Spin left      <-')
            self.motor.spin_left(0.1)
        elif key == KeyCode(char='e'):
            logging.debug('Spin right     ->')
            self.motor.spin_right(0.1)
        else:
            time.sleep(0.1)

    def _on_release(self, key):
        if key != Key.ctrl:
            self.motor.free()
        time.sleep(0.1)

    def listen(self, *args, **kwargs):
        '''
        Function to control the bot using threading. Define the clientSocket in the module before use
        '''
        try:
            with Listener(on_press=self._on_press, on_release=self._on_release) as listener:
                listener.join()
        except KeyboardInterrupt:
            GpioMgmt().release()
            self.headlight.off()
            logging.info("[+] Exiting")
            # clientSocket.close()
            raise e
        except Exception as e:
            GpioMgmt().release()
            self.headlight.off()
            logging.error(str(e))
            # clientSocket.close()
            raise e

    def _run(self):
        self.listen()

    def run(self):
        try:
            GpioMgmt().init_pwm()
            self.ultrasonic.init_pwm()
            self._run()
        except Exception as e:
            GpioMgmt().init_pin()
            logging.error(str(e))


if __name__ == '__main__':
    auto = AutoPilot()
    auto.run()