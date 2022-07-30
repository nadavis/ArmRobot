import logging
from utils.video_stream import VideoStream
from utils.image_processing import ImageProcessing
from PIL import Image
from PIL import ImageTk

class CVOPS():
    def __init__(self, config_manager):

        self.img_processing = ImageProcessing(config_manager.video_stream_config['scale_percent'])
        self.video_stream = VideoStream(1)
        self.target_dim = self.img_processing.get_resize(self.video_stream.shape)
        self.video_stream.set_target_dim(self.target_dim)

    def get_video_size(self):
        return self.target_dim

    def go_to(self):
        print('go to')
        # self.wolrd_coord = [self.x.get(), self.y.get(), self.z.get()]
        # coords, vtheta = self.control_panel.sliders_tab_ui.go_to(self.x.get(), self.y.get(), self.z.get())
        # self.robot_theta = vtheta
        # print('robot theta:', self.robot_theta)

    def get_frame(self, RGB):
        frame = self.video_stream.get_frame(RGB)
        red_only = self.img_processing.get_red_only_rgb(frame)

        # if (self.target_obj.get() == 'RedBox'):
        #     if (len(self.background) > 0):
        #         self.red_background = self.video_stream.img_processing.get_red_only_rgb(self.background)
        #         self.diff_red = self.video_stream.img_processing.calc_motion(self.red_only, self.red_background)
        #         self.diff = ImageTk.PhotoImage(image=Image.fromarray(self.diff_red))
        #         self.diffCanvas.create_image(0, 0, image=self.diff, anchor=tk.NW)
        #         cnts = self.video_stream.img_processing.get_bojects(self.diff_red)
        #         max_rect = 0
        #         for c in cnts:
        #             (x, y, w, h) = cv2.boundingRect(c)
        #             if (w * h > self.min_obj_size):
        #                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #                 if(w*h>max_rect):
        #                     max_rect = w*h
        #                     self.image_coord = [x+w/2, y+h/2]
        #     else:
        #         print('No background frame was set')
        return frame, red_only

    def set_background(self, RGB):
        print('Save background')
        self.background = self.video_stream.get_frame(RGB)
        return self.background

    def find_obj(self, *args):
        print('Find obj: ', self.target_obj.get())
        # self.red_background = self.video_stream.img_processing.get_red_only_rgb(self.background)
        # if (self.target_obj.get() == 'RedBox'):
        #     if (len(self.background) > 0):
        #         self.diff_red = self.video_stream.img_processing.calc_motion(self.red_only, self.red_background)
        #         self.diff = ImageTk.PhotoImage(image=Image.fromarray(self.diff_red))
        #         self.diffCanvas.create_image(0, 0, image=self.diff, anchor=tk.NW)
        #     else:
        #         print('No background frame was set')

    def clear_data(self):
        print('Clear data')
        self.world_coords = []
        self.robot_thetas = []
        self.image_coords = []

    def store_data(self):
        print('Store data')
        if(len(self.world_coords)>0):
            self.world_coords = np.append(self.world_coords, [self.world_coord], axis=0)
        else:
            self.world_coords = [self.world_coord]

        if (len(self.robot_thetas) > 0):
            self.robot_thetas = np.append(self.robot_thetas, [self.robot_theta], axis=0)
        else:
            self.robot_thetas = [self.robot_theta]

        if (len(self.image_coords) > 0):
            self.image_coords = np.append(self.image_coords, [self.image_coord], axis=0)
        else:
            self.image_coords = [self.image_coord]

        print('World: ', self.world_coords)
        print('Robot: ', self.robot_thetas)
        print('Image: ', self.image_coords)
        # x = np.random.randint(-40, 40, size=1)
        # y = np.random.randint(-40, -10, size=1)
        # z = 3
        # coords, vtheta = self.control_panel.sliders_tab_ui.go_to(x, y, z)