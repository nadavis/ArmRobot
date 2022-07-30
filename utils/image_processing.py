import numpy as np
import matplotlib.pyplot as plt
import imutils
import cv2 as cv

class ImageProcessing():
    def __init__(self, scale_percent=20):
        self.scale_percent = scale_percent

    def set_center(self, gray_img):
        row_sum = np.matrix(np.sum(gray_img, 1))
        row_num = np.matrix(np.arange(gray_img.shape[0]))
        row_sum = row_sum.transpose()
        row_mult = np.multiply(row_sum, row_num)
        y_center = np.sum(row_mult)
        total = np.sum(np.sum(gray_img))
        y_center = y_center / total

        column_sum = np.matrix(np.sum(gray_img, 0))
        column_num = np.matrix(np.arange(gray_img.shape[1]))
        column_mult = np.multiply(column_sum, column_num)
        x_center = np.sum(column_mult)
        total = np.sum(np.sum(gray_img))
        x_center = x_center / total

        pos = [x_center, y_center]

        return pos

    def calc_motion(self, current, prev):
        diff = np.int16(np.matrix(current))- np.int16(np.matrix(prev))
        diff[diff<0] = 0
        diff[diff > 255] = 255
        # (score, diff) = structural_similarity(prev, current, full=True)
        # diff = (diff * 255).astype("uint8")

        return np.uint8(diff)

    def get_bojects(self, diff):
        thresh = cv.threshold(diff, 0, 255,
                               cv.THRESH_BINARY | cv.THRESH_OTSU)[1]
        cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
                                cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts


    def get_red_only(self, img):
        r = np.int16((img[:, :, 2]))
        g = np.int16((img[:, :, 1]))
        b = np.int16((img[:, :, 0]))
        red = r - g - b
        red[red < 0] = 0
        red[red > 255] = 255
        self.red_only = np.uint8(red)
        return self.red_only

    def get_red_only_rgb(self, img):
        r = np.int16((img[:, :, 0]))
        g = np.int16((img[:, :, 1]))
        b = np.int16((img[:, :, 1]))
        red = r - g - b
        red[red < 0] = 0
        red[red > 255] = 255
        self.red_only = np.uint8(red)
        return self.red_only

    def get_resize(self, shape):
        width = int(shape[1] * self.scale_percent / 100)
        height = int(shape[0] * self.scale_percent / 100)
        dim = (width, height)
        return dim

    def max_norm_hist(self, hist):
        return 255*hist/max(hist)
