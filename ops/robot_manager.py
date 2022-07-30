from ops.config_ops import ConfigOps
from ops.kinematics_ops import KinematicsOps
from ops.cv_ops import CVOPS
import logging

class RobotManager():
    def __init__(self):
        self.config_ops = ConfigOps()
        self.kinematics_ops = KinematicsOps(self.config_ops)
        self.cv_ops = CVOPS(self.config_ops)

    def get_collision_flg(self):
        return self.config_ops.kinematics_config['enable_collision']

    def get_gripper_state(self):
        return self.config_ops.kinematics_config['gripper_state']

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

    def set_current_angle(self, joint_ind, value):
        self.kinematics_ops.set_current_angle(joint_ind, value)

    def set_collision_state(self, flg):
        self.kinematics_ops.set_collision_state(flg)

    def set_gripper_type(self, type):
        self.kinematics_ops.set_gripper_type(type)

    def open_gripper(self):
        self.kinematics_ops.open_gripper()

    def close_gripper(self):
        self.kinematics_ops.close_gripper()

    def get_frame(self, RGB):
        frame = self.cv_ops.get_frame(RGB)
        return frame

    def set_background(self, RGB):
        frame = self.cv_ops.set_background(RGB)
        return frame

    def get_video_size(self):
        return self.cv_ops.get_video_size()