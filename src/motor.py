import functools
import RPi.GPIO as GPIO
import time

from gpio_mgmt import GpioMgmt
from settings import AUTO
from headlight import HeadLight


IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13

def auto_privilege(func):
    """
    auto pilot 拥有更高权限
    """
    # def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _lock = args[0].lock
        # print(f'[DEBUG] Motor lock: {_lock}')
        _force = kwargs.get('force', False)
        if _lock and not _force:
            return False
        else:
            if _lock and _force:
                _lock = False
            return func(*args, **kwargs)

    return wrapper
    # return decorator


class Motor(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.lock = False
        self.init_motor()
        self.init_headlight()
    
    #电机引脚初始化操作
    def init_motor(self):
        GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)

    def init_headlight(self):
        self.headlight = HeadLight()

    def aquire(self):
        self.lock = True
    
    def release(self):
        self.lock = False

    #小车前进
    @auto_privilege
    def run(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.green()
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车后退
    @auto_privilege
    def back(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.magenta()
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车左转
    @auto_privilege
    def left(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.yellow()
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车右转
    @auto_privilege
    def right(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.yellow()
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车原地左转
    @auto_privilege
    def spin_left(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.yellow()
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车原地右转
    @auto_privilege
    def spin_right(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.yellow()
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车停止
    @auto_privilege
    def brake(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.red()
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)

    #小车自由停车
    @auto_privilege
    def free(self, delaytime=0.1, left_speed=80, right_speed=80, force=False):
        self.headlight.blue()
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        GpioMgmt().pwm_ENA.ChangeDutyCycle(left_speed)
        GpioMgmt().pwm_ENB.ChangeDutyCycle(right_speed)
        time.sleep(delaytime)


