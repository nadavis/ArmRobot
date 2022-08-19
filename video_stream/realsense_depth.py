import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import logging

class DepthCamera:
    def __init__(self, width_target=320):
        self.width_target = width_target
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        self.width = 640
        self.height = 480
        config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 30)

        # Start streaming
        profile = self.pipeline.start(config)
        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        #  clipping_distance_in_meters meters away
        clipping_distance_in_meters = 1  # 1 meter
        clipping_distance = clipping_distance_in_meters / depth_scale

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.shape = [self.height, self.width]
        self.target_dim = self.get_resize_by_width(self.shape)

    def get_resize_by_width(self, shape):
        width = self.width_target
        scale = shape[1] / self.width_target
        height = int(shape[0] / scale)
        dim = (width, height)
        return dim

    def get_frame(self, RGB):
        # frames = self.pipeline.wait_for_frames()
        # depth_frame = frames.get_depth_frame()
        # color_frame = frames.get_color_frame()

        # Get frameset of color and depth
        frames = self.pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = self.align.process(frames)

        # Get aligned frames
        depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        depth_img = np.asanyarray(depth_frame.get_data())
        color_img = np.asanyarray(color_frame.get_data())

        color_img = cv.resize(color_img, self.target_dim)
        color_img = cv.flip(color_img, 1)

        if (RGB):
            color_img = cv.cvtColor(color_img, cv.COLOR_BGR2RGB)

        depth_img = cv.resize(depth_img, self.target_dim)
        depth_img = cv.flip(depth_img, 1)

        cv.imshow("Color frame", depth_img)


        if not depth_frame or not color_frame:
            logging.error("Can't receive frame (stream end?). Exiting ...")
            exit()
            return False, None, None
        return depth_img, color_img

    def release(self):
        self.pipeline.stop()

if __name__ == "__main__":

    dc = DepthCamera()
    cv.namedWindow("Color frame")
    while True:
        depth_frame, color_frame = dc.get_frame(False)

        cv.imshow("depth frame", depth_frame)
        cv.imshow("Color frame", color_frame)
        key = cv.waitKey(1)
        if key == 27:
            break