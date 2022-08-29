import numpy as np
from ops.config_ops import ConfigOps
from ops.kinematics_ops import KinematicsOps
from ops.ArduinoMsgOps import ArduinoMsgOps
from ops.cv_ops import CVOPS
import time
from utils.plot_tools import PlotTools
import math
import logging
from utils.data_buffers import DataBuffer

class RobotManager():
    def __init__(self):
        self.config_ops = ConfigOps()
        self.kinematics_ops = KinematicsOps(self.config_ops)
        self.cv_ops = CVOPS(self.config_ops)
        self.plot_tools = PlotTools(self.config_ops.get_links_size())
        self.arduino_msg_ops = ArduinoMsgOps(self.config_ops)
        self.prev_thetas = self.kinematics_ops.get_home_angles()#np.zeros(self.get_num_of_joints())
        self.thetas = self.kinematics_ops.get_home_angles()#np.zeros(self.get_num_of_joints())
        _, is_collision, H, T = self.kinematics_ops.forward_kinematics(self.thetas)
        self.pos = T[:3, 3]
        self.prev_pos = self.pos.copy()
        # self.circle_coords = self.create_circle_coords()
        # self.coords = self.circle_coords
        self.draw_state = False
        self.run_state = True
        self.calibrate_state = False
        self.transformation_state = False
        self.pixel = np.zeros(3)
        self.zero_draw_structures()
        self.counter = 0
        self.vx = []
        self.vy = []
        self.vz = []
        self.data_buffer = DataBuffer(200, 5, 3, 3, True)

    def get_kinematics_plot(self):
        return self.plot_tools.get_figure()

    def get_config_collision_flg(self):
        return self.config_ops.get_enable_collision_state()

    def get_config_gripper_state(self):
        return self.config_ops.get_gripper_state()

    def get_num_of_joints(self):
        return self.kinematics_ops.get_num_of_joints()

    def get_joint_direction(self, joint_ind):
        return self.kinematics_ops.get_joint_direction(joint_ind)

    def get_min_angle(self, joint_ind):
        return self.kinematics_ops.get_min_angle(joint_ind)

    def get_max_angle(self, joint_ind):
        return self.kinematics_ops.get_max_angle(joint_ind)

    def get_rand_angle(self, joint_ind):
        return self.kinematics_ops.get_rand_angle(joint_ind)

    def get_min_angles(self):
        return self.kinematics_ops.get_min_angles()

    def set_min_angles(self):
        self.thetas = self.kinematics_ops.get_min_angles()

    def get_max_angles(self):
        return self.kinematics_ops.get_max_angles()

    def set_max_angles(self):
        self.thetas = self.kinematics_ops.get_max_angles()

    def get_rand_angles(self):
        return self.kinematics_ops.get_rand_angles()

    def set_rand_angles(self):
        self.thetas = self.kinematics_ops.get_rand_angles()

    def get_home_angle(self):
        return self.kinematics_ops.get_home_angles()

    def set_home_angles(self):
        self.thetas = self.kinematics_ops.get_home_angles()

    def set_span_angles(self):
        self.thetas = self.kinematics_ops.get_span_angles()

    def set_squeeze_angles(self):
        self.thetas = self.kinematics_ops.get_squeeze_angles()

    def set_current_pos(self, pos):
        self.pos = pos

    def get_thetas(self):
        return self.thetas

    def show_kinematics(self, thetas):
        thetas, is_collision, H, T = self.kinematics_ops.forward_kinematics(thetas)
        return self.plot_tools.show_kinematics(H, T)

    def set_collision_state(self, flg):
        self.kinematics_ops.set_collision_state(flg)

    def set_gripper_pos(self, type):
        self.kinematics_ops.set_gripper_pos(type)

    def set_state(self, flg):
        self.run_state = flg
        self.zero_draw_structures()

    def open_gripper(self):
        self.arduino_msg_ops.open_gripper()
        time.sleep(0.1)

    def close_gripper(self):
        self.arduino_msg_ops.close_gripper()
        time.sleep(0.1)

    def get_frame_data(self):
        return self.frame, self.red_only, self.diff_red, self.rect

    def get_depth_frame_data(self):
        return self.frame_depth, self.frame_rgb

    def save_data(self):
        self.data_buffer.save()
        self.data_buffer.save_trans_mat()

    def load_data(self):
        self.data_buffer.load()

    def reset_buffers(self):
        self.data_buffer.reset()

    def set_current_angle(self, joint_ind, theta):
        logging.info('RobotManager: Setting theta %d, ind %d', theta, joint_ind)
        self.thetas[joint_ind] = theta
        # self.kinematics_ops.set_current_angle_by_ind(joint_ind, theta)

    def send_arduino_cmd_msg(self, msg):
        self.arduino_msg_ops.send_cmd_msg(msg)

    def get_arduino_msg(self):
        self.arduino_msg_ops.get_arduino_msg()

    def send_arduino_msg(self, thetas):
        logging.info('RobotManager: Sending thetas %s to arduino with respect to prev thetas %s', str(thetas), str(self.prev_thetas))
        pwm = self.kinematics_ops.angles_2_pwm(thetas)
        self.arduino_msg_ops.send_kinematic_pwm(pwm)

    def is_thetas_changed(self):
        yes = False
        for i in range(len(self.thetas)):
            if(self.prev_thetas[i] != self.thetas[i]):
                yes = True
        return yes

    def is_pos_changed(self):
        yes = False
        for i in range(len(self.pos)):
            if (self.prev_pos[i] != self.pos[i]):
                yes = True
        return yes

    def send_current_angle(self):
        # print('send_current_angle ', self.thetas)
        H = []
        T = []
        if self.is_thetas_changed():
            logging.info('RobotManager: Sending current thetas %s', str(self.thetas))
            self.thetas, is_collision, H, T = self.kinematics_ops.forward_kinematics(self.thetas)
            self.send_arduino_msg(self.thetas)
            self.prev_thetas = self.thetas.copy()
            self.pos = T[:3, 3]
            self.prev_pos = self.pos.copy()
        return self.thetas, H, T

    def send_current_pos(self):
        # print('send_current_pos ', self.pos)
        if self.is_pos_changed():
            logging.info('RobotManager: Sending current pos %s', str(self.pos))
            self.thetas = self.kinematics_ops.run_inv_kinematics(self.pos)
            self.prev_pos = self.pos.copy()
        return self.pos

    def set_calibration(self, world_coord, circle_param):
        if self.cv_ops.get_target_obj() == 'None':
            logging.error('RobotManager: Target object set to %s', self.cv_ops.get_target_obj())
        if self.kinematics_ops.get_gripper_pos() == 'None':
            logging.error('RobotManager: Gripper pos set to %s', self.kinematics_ops.get_gripper_pos())
        background = self.save_background(True)
        self.reset_buffers()
        self.set_draw_param(world_coord, circle_param)
        self.start_draw()
        self.set_calibrate_state(True)

        # if self.draw_state:
        # self.save_data()
        # db.trans_matrix()
        #
        # pos = db.apply_trans_pixel_pos()
        # pixel = db.apply_trans_pos_pixel()

        return background

    def set_calibrate_state(self, state):
        logging.info('RobotManager: Set calibration state %s ', str(state))
        self.calibrate_state = state

    def go_home(self):
        self.thetas = self.kinematics_ops.get_home_angle()
        logging.info('RobotManager: Get home thetas %s ', str(self.thetas))

    def robot_calibration(self):
        if not self.draw_state and self.calibrate_state:
            logging.info('RobotManager: Robot calibration state %d, draw state %d', self.calibrate_state,
                         self.draw_state)
            self.data_buffer.trans_matrix()
            self.save_data()
            self.calibrate_state = False
            self.go_home()

    def robot_run(self):
        self.frame, self.red_only, self.diff_red, self.rect = self.cv_ops.get_frame(True)
        self.frame_depth, self.frame_rgb = self.cv_ops.get_depth_frame(True)
        self.get_coords()
        self.send_current_pos()
        _, H, T = self.send_current_angle()
        b_set = len(H) > 0
        self.store_data(b_set)
        self.robot_calibration()
        self.show_all(b_set, H, T)

        self.counter += 1

    def get_coords(self):
        if self.draw_state:
            self.get_shape_coodrs()
        # else:
        if self.transformation_state:
            self.apply_trans()
            self.transformation_state = False

    def set_transformation_state(self):
        logging.info('RobotManager: Pick %s ', str(self.transformation_state))
        self.open_gripper()
        self.transformation_state = True

    def apply_trans(self):
        if len(self.rect) > 0:
            self.pixel = self.cv_ops.get_pixel_coords(self.rect)
            self.pos = self.data_buffer.apply_trans_pixel_pos(np.array([self.pixel]))

    def store_data(self, b_set):
        if b_set and len(self.rect) > 0:
            self.pixel = self.cv_ops.get_pixel_coords(self.rect)
            self.data_buffer.set(self.thetas, self.pos, self.pixel)

    def save_background(self, RGB):
        frame = self.cv_ops.save_background(RGB)
        return frame

    def get_video_size(self):
        return self.cv_ops.get_video_size()

    def set_target_obj(self, target_obj):
        self.cv_ops.set_target_obj(target_obj)

    def get_min_obj_size(self):
        return self.config_ops.get_min_obj_size()

    def set_draw_param(self, coords, params):
        self.draw_coords = coords
        self.draw_params = params
        self.coords = self.create_circle_coords()

    def create_circle_coords(self):
        x0 = self.draw_coords[0]
        y0 = self.draw_coords[1]
        z0 = self.draw_coords[2]
        rx = self.draw_params[0]
        ry = self.draw_params[1]
        number_of_sample = self.draw_params[2]
        pos_circle = []
        for counter in range(0, number_of_sample):
            x = rx * math.cos(2 * math.pi * counter / number_of_sample) + x0
            y = ry * math.sin(2 * math.pi * counter / number_of_sample) + y0
            pos_circle.append([x, y, z0])
        return pos_circle

    def start_draw(self):
        self.draw_state = True
        self.zero_draw_structures()

    def zero_draw_structures(self):
        self.draw_counter = 0
        self.time_sleep = 100
        self.counter =0

    def show_all(self, b_show, H, T):
        if (b_show):
            self.plot_tools.clean_plot()
            self.plot_tools.show_kinematics(H, T)
            self.plot_tools.draw_circle(self.vx[:self.draw_counter], self.vy[:self.draw_counter],
                                        self.vz[:self.draw_counter])

    def get_shape_coodrs(self):
        self.vx = []
        self.vy = []
        self.vz = []
        ind = self.counter % self.time_sleep
        flg = ind==0 or self.draw_counter==0
        if self.draw_state and flg:
            gripper_state = self.kinematics_ops.get_gripper_pos()
            pos = self.coords[self.draw_counter]
            self.pos = pos.copy()
            logging.info('RobotManager: Drawing circle pos %s, draw counter %s, counter %s', str(pos), str(self.draw_counter), str(self.counter))
            self.draw_counter += 1
            if self.draw_counter == len(self.coords):
                self.draw_state = False
                self.zero_draw_structures()
            self.vx = [x[0] for x in self.coords]
            self.vy = [y[1] for y in self.coords]
            self.vz = [z[2] for z in self.coords]
            if self.draw_counter > 1:
                self.time_sleep = 50
