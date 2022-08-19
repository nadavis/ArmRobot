import logging
from video_stream.video_stream import VideoStream
from video_stream.realsense_depth import DepthCamera
import utils.image_processing as img_p
from PIL import Image
from PIL import ImageTk
import numpy as np
import cv2 as cv

class CVOPS():
    def __init__(self, config_manager):

        self.dc = DepthCamera(config_manager.video_stream_config['width_target'])
        self.video_stream = VideoStream(1, config_manager.video_stream_config['width_target'])
        self.min_obj_size = config_manager.get_min_obj_size()
        self.background = []

    def get_video_size(self):
        return self.video_stream.get_dim()

    def set_target_obj(self, target_obj):
        self.target_obj = target_obj

    def get_target_obj(self):
        return self.target_obj

    def get_depth_frame(self, RGB):
        depth_frame, color_frame = self.dc.get_frame(RGB)
        return depth_frame, color_frame

    def get_frame(self, RGB):
        frame = self.video_stream.get_frame(RGB)
        red_only = img_p.get_red_only_rgb(frame)
        frame, diff_red, rect = self.find_target_obj(frame, red_only)

        return frame, red_only, diff_red, rect

    def find_max_rect(self, rects):
        max_rect = 0
        image_coord = []
        rect = []
        for c in rects:
            (x, y, w, h) = cv.boundingRect(c)
            if (w * h > self.min_obj_size):
                if (w * h > max_rect):
                    max_rect = w * h
                    rect = [x, y, w, h]
                    # image_coord = [x + w / 2, y + h / 2]

        return rect

    def get_pixel_coords(self, rect):
        if len(rect)==0:
            return np.zeros(2)
        x = rect[0]
        y = rect[1]
        w = rect[2]
        h = rect[3]
        z = 0
        out = [x + w / 2, y + h / 2, z]
        logging.info('CVOPS: pixel coords %s ', str(out))
        return out

    def save_background(self, RGB):
        logging.info('CVOPS: Saving background')
        self.background = self.video_stream.get_frame(RGB)
        return self.background

    def find_target_obj(self, frame, red_only):
        diff_red = []
        rect = []
        if (self.target_obj == 'RedBox'):
            if (len(self.background) > 0):
                red_background = img_p.get_red_only_rgb(self.background)
                diff_red = img_p.calc_motion(red_only, red_background)
                rects = img_p.get_rect_objects(diff_red)
                rect = self.find_max_rect(rects)
                # if len(rect)>0:
                #     logging.info('CVOPS: Found target %s objects at %s', self.target_obj, str(rect))
            else:
                logging.warning('CVOPS: No background frame was set')

        return frame, diff_red, rect
