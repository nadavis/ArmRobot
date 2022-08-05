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
        self.prev_thetas = np.zeros(self.get_num_of_joints())
        self.thetas = np.zeros(self.get_num_of_joints())
        _, is_collision, H, T = self.kinematics_ops.forward_kinematics(self.thetas)
        self.pos = T[:3, 3]
        self.prev_pos = self.pos.copy()
        # self.circle_coords = self.create_circle_coords()
        # self.coords = self.circle_coords
        self.draw_state = False
        self.run = True
        self.pixel = np.zeros(3)
        self.zero_draw_structures()
        self.counter = 0
        self.data_buffer = DataBuffer(200, 5, 3, 3)

    # def set_circle_coords(self):
    #     self.coords = self.circle_coords.copy()

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

    def stop(self, flg):
        self.run = flg
        self.zero_draw_structures()

    def open_gripper(self):
        self.arduino_msg_ops.open_gripper()

    def close_gripper(self):
        self.arduino_msg_ops.close_gripper()

    def get_frame_data(self):
        return self.frame, self.red_only, self.diff_red, self.rect

    def save_data(self):
        self.data_buffer.save()

    def load_data(self):
        self.data_buffer.load()

    def reset_buffers(self):
        self.data_buffer.reset()

    def set_current_angle(self, joint_ind, theta):
        logging.info('RobotManager: Setting theta %d, ind %d', theta, joint_ind)
        self.thetas[joint_ind] = theta
        # self.kinematics_ops.set_current_angle_by_ind(joint_ind, theta)

    def send_arduino_msg(self, thetas):
        for i in range(len(thetas)):
            if(self.prev_thetas[i] != thetas[i]):
                pwm = self.kinematics_ops.angle_2_pwm(i, thetas)
                self.arduino_msg_ops.send_kinematic_pwm(i, pwm)
                # self.prev_thetas[i] = thetas[i]

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

    def robot_run(self):
        if self.run:
            self.frame, self.red_only, self.diff_red, self.rect = self.cv_ops.get_frame(True)
            self.draw_shape()
            self.send_current_pos()
            _, H, T = self.send_current_angle()
            if(len(H) > 0):
                if len(self.rect)>0:
                    self.pixel = self.cv_ops.get_pixel_coords(self.rect)
                    self.data_buffer.set(self.thetas, self.pos, self.pixel)
                self.plot_tools.clean_plot()
                self.plot_tools.show_kinematics(H, T)
                self.plot_tools.draw_circle(self.vx[:self.draw_counter], self.vy[:self.draw_counter],
                                                self.vz[:self.draw_counter])
            self.counter += 1

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
            x = rx * math.cos(2 * math.pi * counter / number_of_sample) - x0
            y = ry * math.sin(2 * math.pi * counter / number_of_sample) - y0
            pos_circle.append([x, y, z0])
        return pos_circle

    def start_draw(self):
        self.draw_state = True
        self.zero_draw_structures()

    def zero_draw_structures(self):
        self.draw_counter = 0
        self.time_sleep = 100
        self.counter =0

    def draw_shape(self):
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
                self.time_sleep = 40
