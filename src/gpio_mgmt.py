import RPi.GPIO as GPIO
import time

#设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
#忽略警告信息
GPIO.setwarnings(False)

#小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
#红外避障引脚定义
AvoidSensorLeft = 12
AvoidSensorRight = 17

class GpioMgmt(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.init_motor()
        self.init_infrared()
    
    def init_motor(self):
        pass

    def init_infrared(self):
        pass
    
    def init_pwm(self):
        #设置pwm引脚和频率为2000hz
        self.pwm_ENA = GPIO.PWM(ENA, 2000)
        self.pwm_ENB = GPIO.PWM(ENB, 2000)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)

    #释放GPIO
    def release(self):
        self.pwm_ENA.stop()
        self.pwm_ENB.stop()
        GPIO.cleanup()
