import cv2 as cv
import logging

class VideoStream:
    def __init__(self, camera_id, width_target=320):
        logging.info('VideoStream: Video is opening')
        self.width_target = width_target
        self.video = cv.VideoCapture(camera_id)

        if not self.video.isOpened():
            logging.warning( 'VideoStream: Camera index %d is not available moving to port zero', camera_id)
            self.video = cv.VideoCapture(0)
            if not self.video.isOpened():
                logging.error("Cannot open camera")
                exit()
        self.width = self.video.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height = self.video.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.shape = [self.height, self.width]
        self.target_dim = self.get_resize_by_width(self.shape)
        logging.info('VideoStream: Video resolution is %s', str([self.shape[1], self.shape[0]]))
        logging.info('VideoStream: Resize video resolution is %s', str(self.target_dim))

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    # def set_target_dim(self, target_dim):
    #     self.target_dim = target_dim

    def get_dim(self):
        return self.target_dim

    def get_resize_by_scale(self, shape):
        width = int(shape[1] * self.scale_percent / 100)
        height = int(shape[0] * self.scale_percent / 100)
        dim = (width, height)
        return dim

    def get_resize_by_width(self, shape):
        width = self.width_target
        scale = shape[1] / self.width_target
        height = int(shape[0] / scale)
        dim = (width, height)
        return dim

    def get_frame(self, RGB = False):
        frame = []
        if self.video.isOpened():
            ret, frame = self.video.read()
            if ret:
                frame = cv.resize(frame, self.target_dim)
                frame = cv.flip(frame, 1)
                if (RGB):
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            else:
                return []

            if not ret:
                logging.error("Can't receive frame (stream end?). Exiting ...")
                exit()

        return frame