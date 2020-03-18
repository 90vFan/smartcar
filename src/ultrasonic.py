import RPi.GPIO as GPIO
import time

from gpio_mgmt import GpioMgmt
from infrared import Infrared
from motor import Motor
from headlight import HeadLight


#设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
#忽略警告信息
GPIO.setwarnings(False)
#超声波引脚定义
EchoPin = 0
TrigPin = 1
#舵机引脚定义
ServoPin = 23


class Ultrasonic(object):
    def __init__(self):
        super().__init__()
        self.pwm_servo = None
        self.motor = Motor()
        self.init_utltra()
        self.init_servo()
        self.init_infrared()
        self.init_headlight()
        # self.init_pwm()

    def init_utltra(self):
        """
        电机引脚初始化为输出模式
        按键引脚初始化为输入模式
        超声波引脚初始化
        """
        GPIO.setup(EchoPin, GPIO.IN)
        GPIO.setup(TrigPin, GPIO.OUT)

    def init_servo(self):
        """舵机引脚初始化
        """
        GPIO.setup(ServoPin, GPIO.OUT)

    def init_pwm(self):
        """
        设置舵机的频率和起始占空比
        """
        self.pwm_servo = GPIO.PWM(ServoPin, 50)
        self.pwm_servo.start(0)
    
    def init_infrared(self):
        self.infrared = Infrared() 

    def init_headlight(self):
        self.headlight = HeadLight()

    def detect_distance(self):
        """
        超声波函数
        TrigPin 输入至少10us的高电平信号
        触发超声波模块的测距功能　
        ___|-|____
        模块自动发出８个40kHz的超声波脉冲，并自动检测是否有信号返回
        _____|-|-|-|-|-|-|-|_____
        一旦检测到有回波信号则Echo引脚会输出高电平

        高电平持续时间就是超声波从发射到返回的时间
        """
        # 触发超声波模块测距功能
        GPIO.output(TrigPin, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(TrigPin, GPIO.LOW)
        # 检测回波信号，　一旦检测到有回波信号则Echo引脚会输出高电平
        while not GPIO.input(EchoPin):
            pass
        # start time
        t1 = time.time()
        # 检测高电平持续时间
        while GPIO.input(EchoPin):
            pass
        # end time
        t2 = time.time()
        # S = 高电平时间*声速(340m/s) / 2       (m)
        #                               * 100 (cm)
        distance = ((t2 - t1) * 340 / 2) * 100
        time.sleep(0.01)
        return distance

    def servo_steer(self, pos):
        """
        舵机旋转到指定角度
        """
        # for i in range(18):
        self.pwm_servo.ChangeDutyCycle(2.5 + 10 * pos/180)

    def detect_right_distance(self):
        #舵机旋转到0度，即右侧，测距
        self.servo_steer(0)
        time.sleep(0.8)
        right_distance = self.detect_distance()
        print("[INFO] Ultrasonic detecting ... \nRight distance is %d " % right_distance)
        return right_distance

    def detect_left_distance(self):
        #舵机旋转到180度，即左侧，测距
        self.servo_steer(180)
        time.sleep(0.8)
        left_distance = self.detect_distance()
        print("[INFO] Ultrasonic detecting ... \nLeft distance is %d " % left_distance)
        return left_distance

    def detect_front_distance(self):
        #舵机旋转到90度，即前方，测距
        self.servo_steer(90)
        time.sleep(0.8)
        front_distance = self.detect_distance()
        print("[INFO] Ultrasonic detecting ... \nFront distance is %d " % front_distance)
        return front_distance

    def servo_detect_to_turn_car(self):
        """
        舵机旋转超声波测距避障，led根据车的状态显示相应的颜色
        """
        self.headlight.green()
        right_distance = self.detect_right_distance()
        left_distance = self.detect_left_distance()
        front_distance = self.detect_front_distance()

        if left_distance < 30 and right_distance < 30 and front_distance < 30:
            #亮品红色，掉头
            self.headlight.magenta()
            self.motor.spin_right(left_speed=60, right_speed=60)
            time.sleep(0.004)
        elif left_distance >= right_distance:
            #亮蓝色, 向左转
            self.headlight.yellow()
            self.motor.spin_left(left_speed=60, right_speed=60)
            time.sleep(0.004)
        elif left_distance <= right_distance:
            #亮品红色，向右转
            self.headlight.yellow()
            self.motor.spin_right(left_speed=60, right_speed=60)
            time.sleep(0.004)
    
    def detect_to_turn_car(self):
        front_distance = self.detect_front_distance()

        if front_distance > 50:
            self.infrared.detect_to_turn_car()
            if self.motor.lock:
                self.motor.run(left_speed=100, right_speed=100)
                time.sleep(0.002)
        elif 30 <= front_distance <= 50:
            self.infrared.detect_to_turn_car()
            if self.motor.lock:
                self.motor.run(left_speed=60, right_speed=60)
                time.sleep(0.002)

        elif front_distance < 30:
            self.servo_detect_to_turn_car()
            
        self.motor.free()


if __name__ == '__main__':
    us = Ultrasonic()
    GpioMgmt().init_pwm()
    while True:
        us.motor.lock = True
        us.detect_to_turn_car()
        time.sleep(1)
