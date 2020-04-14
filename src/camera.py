import cv2
import picamera
import numpy as np
import time
import matplotlib.pyplot as plt
from settings import logging


class Camera(object):
    def __init__(self):
        self.cap = self.init_cap()
        self.source = [(100, 300), (540, 300), (0, 420), (640, 420)]
        self.destination = [(170, 250), (460, 250), (170, 420), (460, 420)]

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
            if histr < 3:
                histr = 0
            hist_lane_list.append(histr)
        return hist_lane_list

    def lane_finder(self, frame, hist_lane_list):
        lane_pos = {}

        width = frame.shape[1]
        left_lane_pos = np.argmax(hist_lane_list[0:100])
        right_lane_idx = np.argmax(hist_lane_list[-100:-1])
        right_lane_pos = width - 100 + right_lane_idx if right_lane_idx else width
        center_lane_pos = int((right_lane_pos - left_lane_pos)/2 + left_lane_pos)
        logging.debug(f'Lane position: \n left: {left_lane_pos}, right: {right_lane_pos},'
                      f' center: {center_lane_pos}, width: {width}')

        lane_pos['left'] = left_lane_pos
        lane_pos['right'] = right_lane_pos
        lane_pos['center'] = center_lane_pos
        return lane_pos

    def hist_lane_finder(self, hist_lane_list):
        # length = len(hist_lane_list)
        # half = 
        # for idx in range()
        pass

    def draw_lane(self, frame, lane_pos):
        height = frame.shape[0]
        cv2.line(frame, (lane_pos['left'], 0), (lane_pos['left'], height), [0, 255, 0], 3)
        cv2.line(frame, (lane_pos['right'], 0), (lane_pos['right'], height), [0, 255, 0], 3)
        cv2.line(frame, (lane_pos['center'], 0), (lane_pos['center'], height), [255, 0, 0], 3)

    def get_deviation(self, theta, width, lane_pos):
        frame_center_pos = 145
        deviation = lane_pos['center'] - frame_center_pos
        delta = lane_pos['right'] - lane_pos['left']
        if theta != np.pi/2 and \
            (lane_pos['left'] == 0 or \
             lane_pos['right'] == width or \
             delta >= 260 or \
             delta <= 180):
            angle = 180 * (theta / np.pi)
            logging.debug(f'Correct deviation with theta angle {int(angle)}')
            deviation = np.cos(theta) * 30
        deviation = int(deviation)
        logging.debug(f'deviation: {deviation}')
        return deviation

    def deviation_finder(self, frame_edge):
        hist_lane_list = self.histogram(frame_edge)
        # lane
        lane_pos = self.lane_finder(frame_edge, hist_lane_list)
        theta, lines = self.get_hough_lines(frame_edge)
        width = frame_edge.shape[1]
        deviation = self.get_deviation(theta, width, lane_pos)
        return deviation, lane_pos, lines

    def draw_deviation(self, frame, deviation):
        turn = 'C'
        if deviation > 5: 
            turn = 'R'
        elif deviation < -5:
            turn = 'L'
        text = f'dev={deviation} {turn}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, org=(80, 25),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 0, 255),
                    thickness=2)

    def draw_hough_lines(self, frame, lines):
        if lines is None:
            return

        for theta, rho in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),1)

    def filter_hsv(self, frame_hsv):
        lower = np.array([100, 40, 100])
        upper = np.array([200, 150, 200])
        mask = cv2.inRange(frame_hsv, lower, upper)
        frame_output = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
        # frame_output = cv2.cvtColor(frame_output, cv2.COLOR_HSV2RGB)
        return frame_output

    def get_hough_lines(self, frame_edge):
        max_theta = np.pi / 2
        max_rho = 0
        lines = cv2.HoughLines(frame_edge,1,np.pi/180, threshold=80)
        if lines is not None:
            for rho,theta in lines[0]:
                logging.debug(f'houghlines: {rho}, {theta}')
                if np.abs(theta - np.pi/2) > np.abs(max_theta - np.pi/2):
                    max_theta = theta
                    max_rho = rho

            angle = 180 * (max_theta / np.pi)
            logging.debug(f'max theta angle {int(angle)}')

        return max_theta, lines

    def color_process(self, frame_hsv):
        # frame_hsv = self.filter_hsv(frame_hsv)
        frame_gray = cv2.cvtColor(frame_hsv, cv2.COLOR_RGB2GRAY)
        return frame_hsv, frame_gray

    def transform_process(self, frame_gray):
        frame_pers_init = self.perpective(frame_gray)
        frame_pers_crop = frame_pers_init[210:420, 165:465] # height, width
        frame_pers_final = cv2.Sobel(frame_pers_crop, cv2.CV_8U, 1, 0, ksize=3)
        # frame_pers_final = cv2.morphologyEx(frame_pers_crop, cv2.MORPH_CLOSE, (10, 10))
        return frame_pers_final

    def thresh_process(self, frame_pers_final):
        logging.debug(f'denoising {frame_pers_final.shape}')
        # threshold
        frame_thresh = cv2.inRange(frame_pers_final, 40, 225)
        frame_thresh = frame_pers_final
        # frame_thresh = cv2.GaussianBlur(frame_thresh, (5, 5), 2)
        frame_thresh = cv2.dilate(frame_thresh, (5, 5), iterations=5)
        # frame_thresh = cv2.morphologyEx(frame_thresh, cv2.MORPH_CLOSE, (5,5), iterations=10)

        # canny
        frame_canny = cv2.Canny(frame_pers_final, 40, 225, None, 3, False)
        frame_canny = cv2.morphologyEx(frame_canny, cv2.MORPH_CLOSE, (5, 5), iterations=5)

        # edge
        canny_mask_inv = cv2.bitwise_not(frame_canny)
        thresh_mask_inv = cv2.bitwise_not(frame_thresh)
        mask_inv = canny_mask_inv + thresh_mask_inv
        frame_edge = cv2.bitwise_and(frame_canny, frame_thresh, mask=cv2.bitwise_not(mask_inv))
        # frame_edge = cv2.dilate(frame_edge, (5, 5), iterations=5)
        # frame_edge = cv2.morphologyEx(frame_edge, cv2.MORPH_OPEN, (5, 5), iterations=3)
        # frame_edge = cv2.GaussianBlur(frame_edge, (5, 5), 5)
        _, frame_edge = cv2.threshold(frame_edge, 0, 125, cv2.THRESH_BINARY)

        return frame_thresh, frame_canny, frame_edge

    def display_original(self, frame):
        """original view with view box
        """
        self.setup_window(frame, "Original", px=0, py=50)

    def display_hsv(self, frame_hsv):
        self.setup_window(frame_hsv, "Original", px=0, py=50)

    def display_thresh_hsv(self, frame_hsv):
        self.draw_line_box(frame_hsv)
        self.setup_window(frame_hsv, "HSV", px=0, py=530)

    def display_gray(self, frame_gray):
        # gray view
        self.setup_window(frame_gray, "Gray", px=640, py=530)

    def display_edge(self, frame_pers_final, frame_thresh, frame_canny, frame_edge):
        """frame_pers_final.shape (210x300) !!!
        """
        frame_pers_final_copy = frame_pers_final.copy()
        self.put_text(frame_pers_final_copy, 'Perspective')
        self.put_text(frame_edge, 'Edge')
        image_row_1 = np.hstack([frame_pers_final_copy, frame_edge])

        self.put_text(frame_thresh, 'Thresh')
        self.put_text(frame_canny, 'Canny')
        image_row_2 = np.hstack([frame_thresh, frame_canny])

        image_quarter = np.vstack([image_row_1, image_row_2])

        self.setup_window(image_quarter, "Edge", px=640, py=50)

    def put_text(self, frame, text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, org=(100, 25),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(255, 0, 0),
                    thickness=1)

    def display_lane(self, frame_pers_final, lane_pos, deviation, lines):
        contours, hierarchy = cv2.findContours(frame_pers_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame_pers_final, contours, -1, (0,255,0), 3)
        frame_lane = cv2.cvtColor(frame_pers_final, cv2.COLOR_GRAY2RGB)

        self.draw_hough_lines(frame_lane, lines)
        self.draw_lane(frame_lane, lane_pos)
        self.draw_deviation(frame_lane, deviation)
        

        self.setup_window(frame_lane, "Lane", px=640, py=530)

    def analyze(self):
        success, frame = self.cap.read()
        # self.display_original(frame)
        # logging.debug(f'denoising {frame.dtype} {frame.shape}')
        # # frame = cv2.fastNlMeansDenoisingColored(frame, templateWindowSize=5,
        #                                               searchWindowSize=5,
        #                                               h=7,
        #                                               hColor=21)
        # logging.debug(f'denoising {frame.shape}')

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        self.display_hsv(frame_hsv)

        frame_thresh_hsv, frame_gray = self.color_process(frame_hsv)
        # frame_gray = cv2.equalizeHist(frame_gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        frame_gray = clahe.apply(frame_gray)
        self.display_thresh_hsv(frame_thresh_hsv)
        # self.display_gray(frame_gray)

        frame_pers_final = self.transform_process(frame_gray)
        frame_thresh, frame_canny, frame_edge = self.thresh_process(frame_pers_final)
        deviation, lane_pos, lines = self.deviation_finder(frame_edge)
        self.display_edge(frame_pers_final, frame_thresh, frame_canny, frame_edge)        
        self.display_lane(frame_pers_final, lane_pos, deviation, lines)

        return deviation

    def analyze_hist(self):
        success, frame = self.cap.read()
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        # frame_hsv, frame_gray = self.color_process(frame_hsv)
        plt.figure(figsize=(24, 10))
        self.display_histogram(frame_hsv)
        cdf, cdf_normalized = self.calc_cdf(frame_hsv)
        self.display_cdf(frame_hsv, cdf_normalized)
        self.hist_normal(frame_hsv, cdf)
        # img = frame_gray
        # img_equ = cv2.equalizeHist(img)
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        # img_clahe = clahe.apply(img)
        # plt.subplot(131)
        # plt.imshow(img)
        # plt.subplot(132)
        # plt.imshow(img_equ)
        # plt.subplot(133)
        # plt.imshow(img_clahe)

        plt.show()

    def display_histogram(self, img):
        plt.subplot(221)
        color = ('r','g','b')
        for i,col in enumerate(color):
            histr = cv2.calcHist([img],[i],None,[256],[0,256])
            plt.plot(histr, color=col, )
            plt.xlim([0,256])
        plt.legend(['h', 's', 'v'])

    def calc_cdf(self, img):
        hist,bins = np.histogram(img.flatten(),256,[0,256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * float(hist.max()) / cdf.max()
        return cdf, cdf_normalized

    def display_cdf(self, img, cdf_normalized):
        plt.subplot(222)
        plt.plot(cdf_normalized, color = 'b')
        plt.hist(img.flatten(),256,[0,256], color = 'r')
        plt.xlim([0,256])
        plt.legend(('cdf','histogram'), loc = 'upper left')

    def hist_normal(self, img, cdf):
        cdf_m = np.ma.masked_equal(cdf,0)
        cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
        cdf = np.ma.filled(cdf_m,0).astype('uint8')
        img_equ = cdf[img]

        # img_equ = cv2.equalizeHist(img)
        plt.subplot(223)
        plt.imshow(img)
        plt.subplot(224)
        plt.imshow(img_equ)


    def run(self):
        while self.cap.isOpened():
            self.analyze()
            # self.analyze_hist()
            # break


if __name__ == '__main__':
    cam = Camera()
    cam.run()
