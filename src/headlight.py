import RPi.GPIO as GPIO
import time

from gpio_mgmt import GpioMgmt
from settings import logging


# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
# 忽略警告信息
GPIO.setwarnings(False)
#RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24

HIGH = GPIO.HIGH
LOW = GPIO.LOW


class HeadLight(object):
    def __init__(self):
        self.init_led()

    def init_led(self):
        """RGB三色灯引脚初始化
        """
        GPIO.setup(LED_R, GPIO.OUT)
        GPIO.setup(LED_G, GPIO.OUT)
        GPIO.setup(LED_B, GPIO.OUT)

    def off(self):
        self._apply(LOW, LOW, LOW)

    def red(self):
        self._apply(HIGH, LOW, LOW)

    def magenta(self):
        """品红色
        """
        self._apply(HIGH, LOW, HIGH)

    def blue(self):
        self._apply(LOW, LOW, HIGH)

    def green(self):
        self._apply(LOW, HIGH, LOW)

    def yellow(self):
        self._apply(HIGH, HIGH, LOW)

    def color(self, color=None):
        if color == 'green':
            self._apply(LOW, HIGH, LOW)
        else:
            self._apply(LOW, LOW, LOW)

    def _apply(self, R, G, B):
        GPIO.output(LED_R, R)
        GPIO.output(LED_G, G)
        GPIO.output(LED_B, B)
