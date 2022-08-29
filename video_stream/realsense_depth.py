import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import logging

class DepthCamera:
    def __init__(self, fps, width_target=320):
        self.width_target = width_target
        self.pipeline = rs.pipeline()
        config = rs.config()
        self.is_opened = False

        try:
            # Get device product line for setting a supporting resolution
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = config.resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))
            logging.info("Opening depth camera")
            self.is_opened = True
        except:
            logging.error("Cannot open depth camera")

        if self.is_opened:
            self.width = 640
            self.height = 480
            config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, fps)
            config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, fps)

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

    def __del__(self):
        if self.is_opened:
            self.pipeline.stop()

    def get_resize_by_width(self, shape):
        width = self.width_target
        scale = shape[1] / self.width_target
        height = int(shape[0] / scale)
        dim = (width, height)
        return dim

    def filter(self, depth_frame):
        # Apply filter to fill the Holes in the depth image
        spatial = rs.spatial_filter()
        spatial.set_option(rs.option.holes_fill, 3)
        filtered_depth = spatial.process(depth_frame)

        hole_filling = rs.hole_filling_filter()
        filled_depth = hole_filling.process(filtered_depth)
        return filled_depth

    def get_frame(self, RGB):
        if self.is_opened:
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

            # depth_frame = self.filter(depth_frame)

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
                return [], []
            return depth_img, color_img
        else:
            return [], []

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