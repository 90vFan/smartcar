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


# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
# 忽略警告信息
GPIO.setwarnings(False)


class KeyPilot(object):
    """
    Control smart car with Keyboard input
    """
    def __init__(self):
        self.init_motor()
        self.init_infrared()
        self.init_ultrasonic()
        self.init_headlight()

    def init_motor(self):
        self.motor = Motor()

    def init_infrared(self):
        self.infrared = Infrared()

    def init_headlight(self):
        self.headlight = HeadLight()

    def init_ultrasonic(self):
        self.ultrasonic = Ultrasonic()

    def detect_to_turn(self):
        self.motor.aquire()
        block = self.ultrasonic.detect_to_turn_car()
        self.motor.release()
        return block

    def _on_press(self, key):
        logging.debug(f'Press {key}')
        block = self.detect_to_turn()

        # if self.motor.lock:
        #     pass
        # if block:
        #     pass
        # else:
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
        elif key == Key.space:
            logging.debug('Brake          X')
            self.motor.brake(0.1)
        else:
            time.sleep(0.1)

    def _on_release(self, key):
        logging.debug(f'Press {key}')
        # if self.motor.lock:
        #     pass
        # else:
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

    def run(self):
        try:
            GpioMgmt().init_pwm()
            self.ultrasonic.init_pwm()
            self.detect_to_turn()
            self.listen()
        except Exception as e:
            GpioMgmt().init_pin()
            logging.error(str(e))


if __name__ == "__main__":
    kp = KeyPilot()
    kp.run()