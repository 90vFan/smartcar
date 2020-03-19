import argparse

from gpio_mgmt import GpioMgmt
from key_pilot import KeyPilot
from settings import logging


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='Pilot mode: auto, key')
args = parser.parse_args()


try:
    if args.mode == 'auto':
        pass
    if args.mode == 'key':
        kp = KeyPilot()
        kp.run()
except Exception as e:
    logging.error(f'[ERROR] fail to run in key mode: {e}')
    GpioMgmt().release()
