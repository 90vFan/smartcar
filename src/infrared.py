import RPi.GPIO as GPIO
import time

from gpio_mgmt import GpioMgmt
from motor import Motor


#设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)
#忽略警告信息
GPIO.setwarnings(False)
#红外避障引脚定义
AvoidSensorLeft = 12
AvoidSensorRight = 17


class Infrared(object):
    def __init__(self):
        super().__init__()
        self.motor = Motor()
        self.init_sensor()
    
    def init_sensor(self):
        GPIO.setup(AvoidSensorLeft, GPIO.IN)
        GPIO.setup(AvoidSensorRight, GPIO.IN)

    def detect_to_turn_car(self):
        #遇到障碍物,红外避障模块的指示灯亮,端口电平为LOW
        #未遇到障碍物,红外避障模块的指示灯灭,端口电平为HIGH
        left_sensor = GPIO.input(AvoidSensorLeft)
        right_sensor = GPIO.input(AvoidSensorRight)
        print(f'[DEBUG] Infra red detecting ... \nleft: {left_sensor} right: {right_sensor}')
        if left_sensor == True and right_sensor == True:
            if self.motor.lock:
                self.motor.run()  # 当两侧均未检测到障碍物时调用前进函数
            return False
        else:
            self.motor.lock = True
            if left_sensor == True and right_sensor == False:
                self.motor.spin_left(force=True)  # 右边探测到有障碍物，有信号返回，原地向左转
                time.sleep(0.002)
            elif right_sensor == True and left_sensor == False:
                self.motor.spin_right(force=True)  # 左边探测到有障碍物，有信号返回，原地向右转
                time.sleep(0.002)
            elif right_sensor == False and left_sensor == False:
                self.motor.spin_right(force=True)  # 当两侧均检测到障碍物时调用固定方向的避障(原地右转)
                time.sleep(0.002)
            self.motor.free()
            self.motor.lock = False

        return True

if __name__ == '__main__':
    ifr = Infrared()
    GpioMgmt().init_pwm()
    while True:
        ifr.motor.lock = True
        ifr.detecting()
        time.sleep(0.5)
