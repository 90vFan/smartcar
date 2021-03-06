"""test_2_mac_receive_images.py -- receive & display image stream.

A simple test program that uses imagezmq to receive an image stream from
a Raspberry Pi and display it as a video steam.

1. Run this program in its own terminal window on the mac:
python test_2_mac_receive_images.py

This "receive and display images" program must be running before starting
the RPi sending program.

2. Run the image sending program on the RPi:
python test_2_rpi_send_images.py

A cv2.imshow() window will appear on the Mac showing the tramsmitted images
as a video stream. You can repeat Step 2 and start the test_2_rpi_send_images.py
on multiple RPis and each one will cause a new cv2.imshow() window to open.

To end the programs, press Ctrl-C in the terminal window of the RPi  first.
Then press Ctrl-C in the terminal window of the receiving proram. You may have
to press Ctrl-C in the display window as well.
"""
import sys

import cv2
import imagezmq
import imutils
import numpy as np

def filter_hsv(frame_hsv):
    lower = np.array([100, 40, 100])
    upper = np.array([200, 200, 200])
    mask = cv2.inRange(frame_hsv, lower, upper)
    mask_inv = cv2.bitwise_not(mask)
    frame_output = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
    # frame_output = cv2.cvtColor(frame_output, cv2.COLOR_HSV2RGB)
    return frame_output

image_hub = imagezmq.ImageHub()
while True:  # show streamed images until Ctrl-C
    rpi_name, image = image_hub.recv_image()
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    image_filter = filter_hsv(image_hsv)
    cv2.imshow(rpi_name, np.hstack([image, image_hsv, image_filter]))  # 1 window for each RPi
    cv2.waitKey(1)
    image_hub.send_reply(b'OK')
