import logging
from utils.video_stream import VideoStream
from utils.image_processing import ImageProcessing
from PIL import Image
from PIL import ImageTk
import numpy as np
import cv2 as cv

class CVOPS():
    def __init__(self, config_manager):

        self.img_processing = ImageProcessing()
        self.video_stream = VideoStream(1, config_manager.video_stream_config['width_target'])
        self.min_obj_size = config_manager.get_min_obj_size()
        self.background = []

    def get_video_size(self):
        return self.video_stream.get_dim()

    # def go_to(self):
    #     print('go to')
    #     # self.wolrd_coord = [self.x.get(), self.y.get(), self.z.get()]
    #     # coords, vtheta = self.control_panel.sliders_tab_ui.go_to(self.x.get(), self.y.get(), self.z.get())
    #     # self.robot_theta = vtheta
    #     # print('robot theta:', self.robot_theta)

    def set_target_obj(self, target_obj):
        self.target_obj = target_obj

    def get_frame(self, RGB):
        frame = self.video_stream.get_frame(RGB)
        red_only = self.img_processing.get_red_only_rgb(frame)
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
        return [x + w / 2, y + h / 2, z]

    def save_background(self, RGB):
        logging.info('CVOPS: Saving background')
        self.background = self.video_stream.get_frame(RGB)
        return self.background

    def find_target_obj(self, frame, red_only):
        diff_red = []
        rect = []
        if (self.target_obj == 'RedBox'):
            if (len(self.background) > 0):
                red_background = self.img_processing.get_red_only_rgb(self.background)
                diff_red = self.img_processing.calc_motion(red_only, red_background)
                rects = self.img_processing.get_rect_objects(diff_red)
                rect = self.find_max_rect(rects)
                # if len(rect)>0:
                #     logging.info('CVOPS: Found target %s objects at %s', self.target_obj, str(rect))
            else:
                logging.error('CVOPS: No background frame was set')

        return frame, diff_red, rect

    # def clear_data(self):
    #     print('Clear data')
    #     self.world_coords = []
    #     self.robot_thetas = []
    #     self.image_coords = []

    # def store_data(self):
    #     print('Store data')
    #     if(len(self.world_coords)>0):
    #         self.world_coords = np.append(self.world_coords, [self.world_coord], axis=0)
    #     else:
    #         self.world_coords = [self.world_coord]
    #
    #     if (len(self.robot_thetas) > 0):
    #         self.robot_thetas = np.append(self.robot_thetas, [self.robot_theta], axis=0)
    #     else:
    #         self.robot_thetas = [self.robot_theta]
    #
    #     if (len(self.image_coords) > 0):
    #         self.image_coords = np.append(self.image_coords, [self.image_coord], axis=0)
    #     else:
    #         self.image_coords = [self.image_coord]
    #
    #     print('World: ', self.world_coords)
    #     print('Robot: ', self.robot_thetas)
    #     print('Image: ', self.image_coords)
    #     # x = np.random.randint(-40, 40, size=1)
    #     # y = np.random.randint(-40, -10, size=1)
    #     # z = 3
    #     # coords, vtheta = self.control_panel.sliders_tab_ui.go_to(x, y, z)