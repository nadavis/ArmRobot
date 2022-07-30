import cv2 as cv

class VideoStream:
    def __init__(self, camera_id):
        print("Open camera")
        self.video = cv.VideoCapture(camera_id)

        if not self.video.isOpened():
            print('Defult camera zero')
            self.video = cv.VideoCapture(0)
            if not self.video.isOpened():
                print("Cannot open camera")
                exit()
        self.width = self.video.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height = self.video.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.shape = [self.height, self.width]

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def set_target_dim(self, target_dim):
        self.target_dim = target_dim

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
                print("Can't receive frame (stream end?). Exiting ...")
                exit()

        return frame