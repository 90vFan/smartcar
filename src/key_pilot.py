from pynput.keyboard import Key, Listener
import time
import os

from gpio_mgmt import GpioMgmt
from motor import Motor
from infrared import Infrared
from ultrasonic import Ultrasonic
from headlight import HeadLight


class KeyPilot(object):
    """
    Control smart car with Keyboard input
    """
    def __init__(self):
        super().__init__()
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

    def infrared_detect(self):
        block = self.infrared.detect_to_turn_car()
        return block

    def detect(self):
        self.motor.lock = False
        self.ultrasonic.detect_to_turn_car()
        # self.infrared_detect()

    def _on_press(self, key):
        print(f'[DEBUG] Press {key}')
        if self.motor.lock:
            pass
        if self.detect():
            self.motor.free()
        else:
            if key == Key.up:
                print('[DEBUG] Run forward   ^')
                self.motor.run(0.1)
            elif key == Key.down:
                print('[DEBUG] Run backward  _')
                self.motor.back(0.1)
            elif key == Key.left:
                print('[DEBUG] Run left      <-')
                self.motor.left(0.1)
            elif key == Key.right:
                print('[DEBUG] Run right     ->')
                self.motor.right(0.1)
            elif key == Key.space:
                print('[DEBUG] Brake          X')
                self.motor.brake(0.1)
            else:
                time.sleep(0.1)

    def _on_release(self, key):
        print(f'[DEBUG] Press {key}')
        if self.motor.lock:
            pass
        else:
            if key == Key.up:
                self.motor.free()
            elif key == Key.down:
                self.motor.free()
            elif key == Key.left:
                self.motor.free()
            elif key == Key.right:
                self.motor.free()
            elif key == Key.space:
                self.motor.free()
            else:
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
            print("[+] Exiting")
            # clientSocket.close()
            raise e
        except Exception as e:
            GpioMgmt().release()
            self.headlight.off()
            print("[ERROR] :", str(e))
            # clientSocket.close()
            raise e

    def run(self):
        try:
            GpioMgmt().init_pwm()
            self.ultrasonic.init_pwm()
            self.motor.lock = False
            self.detect()
            self.listen()
        except Exception as e:
            os.system('./initpin.sh')
            print("[ERROR] :", str(e))


if __name__ == "__main__":
    kp = KeyPilot()
    kp.run()