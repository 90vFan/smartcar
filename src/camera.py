import cv2
import picamera
import numpy as np
# import matplotlib.pyplot as plt
from settings import logging


class Camera(object):
    def __init__(self):
        self.cap = self.init_cap()
        self.source = [(150, 300), (470, 300), (50, 420), (570, 420)]
        self.destination = [(170, 250), (450, 250), (170, 420), (450, 420)]

    def init_cap(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap

    def setup_window(self, frame, name="Image", px=0, py=50):
        height, width = 640, 480
        cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow(name, px, py)
        cv2.resizeWindow(name, height, width)

        cv2.imshow(name, frame)
        cv2.waitKey(1)

    def draw_line_box(self, frame):
        source = self.source
        cv2.line(frame, source[0], source[1], (0, 0, 255), 2)
        cv2.line(frame, source[1], source[3], (0, 0, 255), 2)
        cv2.line(frame, source[3], source[2], (0, 0, 255), 2)
        cv2.line(frame, source[2], source[0], (0, 0, 255), 2)

        destination = self.destination
        cv2.line(frame, destination[0], destination[1], (0, 255, 0), 2)
        cv2.line(frame, destination[1], destination[3], (0, 255, 0), 2)
        cv2.line(frame, destination[3], destination[2], (0, 255, 0), 2)
        cv2.line(frame, destination[2], destination[0], (0, 255, 0), 2)

    def perpective(self, frame):
        source = np.float32(self.source)
        destination = np.float32(self.destination)
        matrix = cv2.getPerspectiveTransform(source, destination);
        frame_pers = cv2.warpPerspective(frame, matrix, (640, 480))
        return frame_pers

    def histogram(self, frame):
        hist_lane_list = []
        for i in range(0, 301):
            # frame.shape (210x300)
            roi = frame[110:210, i:i+1].ravel()
            histr = int(sum(roi / 255))
            if histr < 5:
                histr = 0
            hist_lane_list.append(histr)
        return hist_lane_list

    def lane_finder(self, frame):
        width = frame.shape[1]
        hist_lane_list = self.histogram(frame)
        left_lane_pos = np.argmax(hist_lane_list[0:100])
        right_lane_idx = np.argmax(hist_lane_list[-100:-1])
        right_lane_pos = width - 100 + right_lane_idx if right_lane_idx else width
        center_lane_pos = int((right_lane_pos - left_lane_pos)/2 + left_lane_pos)
        logging.debug(f'Lane position: \n left: {left_lane_pos}, right: {right_lane_pos}, center: {center_lane_pos}')
        return left_lane_pos, right_lane_pos, center_lane_pos

    def draw_lane(self, frame, left_lane_pos, right_lane_pos, center_lane_pos):
        height = frame.shape[0]
        cv2.line(frame, (left_lane_pos, 0), (left_lane_pos, height), [0, 255, 0], 3)
        cv2.line(frame, (right_lane_pos, 0), (right_lane_pos, height), [0, 255, 0], 3)
        cv2.line(frame, (center_lane_pos, 0), (center_lane_pos, height), [255, 0, 0], 3)

    def get_deviation(self, frame, left_lane_pos, right_lane_pos, center_lane_pos):
        width = frame.shape[1]
        frame_center_pos = 145
        deviation = center_lane_pos - frame_center_pos

        logging.debug(f'deviation: {deviation}')
        return deviation

    def draw_deviation(self, frame, deviation):
        text = f'dev={deviation}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, org=(100, 25),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 0, 255),
                    thickness=2)

    def filter_hsv(self, frame):
        lower = np.array([100, 70, 100])
        upper = np.array([200, 200, 200])
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(frame_hsv, lower, upper)
        frame_output = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
        # frame_output = cv2.cvtColor(frame_output, cv2.COLOR_HSV2RGB)
        return frame_output

    def analyze(self, display={}):
        success, frame = self.cap.read()
        # original view with view box
        frame = self.filter_hsv(frame)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        self.draw_line_box(frame)
        self.setup_window(frame, "Original", px=0, py=50)
        # gray view
        # self.setup_window(frame_gray, "Gray", px=0, py=530)
        # perspective view in gray mode
        frame_pers_init = self.perpective(frame_gray)
        # self.setup_window(frame_pers, "Perspective", px=0, py=530)
        frame_pers_crop = frame_pers_init[210:420, 165:465] # height, width
        frame_pers_final = cv2.Sobel(frame_pers_crop, cv2.CV_8U, 1, 0, ksize=3)
        # frame_pers_final = cv2.morphologyEx(frame_pers_crop, cv2.MORPH_CLOSE, (10, 10))
        # frame_pers_final.shape (210x300) !!!
        if display.get('perspective', False):
            self.setup_window(frame_pers_final, "Perspective Crop", px=0, py=530)
        # threshold
        frame_thresh = cv2.inRange(frame_pers_final, 50, 140)
        frame_thresh = cv2.morphologyEx(frame_thresh, cv2.MORPH_OPEN, (5,5), iterations=3)
        if display.get('thresh', False):
            self.setup_window(frame_thresh, "Thresh", px=640, py=530)
        # canny
        frame_canny = cv2.Canny(frame_pers_final, 50, 100, None, 3, False)
        frame_canny = cv2.morphologyEx(frame_canny, cv2.MORPH_CLOSE, (5, 5), iterations=5)
        if display.get('canny', False):
            self.setup_window(frame_canny, "Canny", px=1280, py=530)
        # edge
        canny_mask_inv = cv2.bitwise_not(frame_canny)
        thresh_mask_inv = cv2.bitwise_not(frame_thresh)
        mask_inv = canny_mask_inv + thresh_mask_inv
        frame_edge = cv2.bitwise_and(frame_canny, frame_thresh, mask=cv2.bitwise_not(mask_inv))

        # frame_edge = cv2.morphologyEx(frame_edge, cv2.MORPH_OPEN, (5, 5), iterations=3)
        frame_edge = cv2.GaussianBlur(frame_edge, (5, 5), 5)
        _, frame_edge = cv2.threshold(frame_edge, 0, 125, cv2.THRESH_BINARY)

        #frame_edge = frame_canny + frame_thresh
        self.setup_window(frame_edge, "Edge", px=640, py=50)
        # lane
        left_lane_pos, right_lane_pos, center_lane_pos = self.lane_finder(frame_edge)
        frame_lane = cv2.cvtColor(frame_pers_final, cv2.COLOR_GRAY2RGB)
        self.draw_lane(frame_lane, left_lane_pos, right_lane_pos, center_lane_pos)
        deviation = self.get_deviation(frame_lane, left_lane_pos, right_lane_pos, center_lane_pos)
        self.draw_deviation(frame_lane, deviation)
        self.setup_window(frame_lane, "Lane", px=1280, py=50)

        return deviation

    def run(self):
        while self.cap.isOpened():
            display = {'perspective': True, 'canny': True, 'thresh': True}
            self.analyze(display)


if __name__ == '__main__':
    cam = Camera()
    cam.run()