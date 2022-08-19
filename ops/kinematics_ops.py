# from utils.servo_convertor import ServoConvertor
from utils.plot_tools import PlotTools
from kinematics.arm_kinematics import ArmKinematics
from arduino.arduino_msg import ArduinoMsg
import numpy as np
import random
import logging


class KinematicsOps():
    def __init__(self, config_manager):
        # self.servo_convertor = ServoConvertor(config_manager.servo_config)

        # self.plot_tools = PlotTools(config_manager.kinematics_config['link_size'])

        self.arm_kinematics = ArmKinematics(config_manager)
        self.max_angle_motor_spec = np.array(config_manager.get_angle_max())
        self.max_motor_spec = np.array(config_manager.get_pwm_max())
        self.gear_spec = np.array(config_manager.get_servo_gear_ratio())
        self.min_motor_spec = np.array(config_manager.get_pwm_min())
        self.pwm2angle = self.max_angle_motor_spec / (self.gear_spec * (self.max_motor_spec - self.min_motor_spec))
        self.home_pwm = np.array(config_manager.get_servo_home())
        self.min_pwm = np.array(config_manager.get_servo_min())
        self.max_pwm = np.array(config_manager.get_servo_max())
        self.servo_direction = np.array(config_manager.get_servo_direction())

        # self.is_collision = False
        self.enable_collision = config_manager.get_enable_collision_state()
        self.gripper_pos = config_manager.get_gripper_state()
        self.thetas = config_manager.get_thetas_zero()
        self.prev_thetas = np.zeros(self.get_num_of_joints())
        self.pwm = []

    def get_num_of_joints(self):
        num_of_dof = self.arm_kinematics.get_number_of_dof()
        logging.info('KinematicsOps: Getting number of dof, number of dof is: %d', num_of_dof)
        return num_of_dof

    def get_joint_direction(self, joint_ind):
        value = self.servo_direction[joint_ind]
        logging.info('KinematicsOps: Getting direction joint is: %d for joint number: %d', value, joint_ind)
        return value

    def get_min_angle(self, joint_ind):
        value = self.pwm_2_angle(joint_ind, self.min_pwm)
        logging.info('KinematicsOps: Getting min value: %.4f for joint number: %d', value, joint_ind)
        return value

    def get_max_angle(self, joint_ind):
        value = self.pwm_2_angle(joint_ind, self.max_pwm)
        logging.info('KinematicsOps: Getting max value: %.4f for joint number: %d', value, joint_ind)
        return value

    def pwm_2_angle(self, ind, val):
        value = (val[ind]-self.home_pwm[ind])*self.pwm2angle[ind]
        logging.info('KinematicsOps: Converting, PWM value: %d to angle value: %.4f for joint number: %d', val[ind], value, ind)
        return value

    def angle_2_pwm(self, val):
        val = val * self.servo_direction[:-1]
        value = self.home_pwm[:-1]+val/self.pwm2angle[:-1]
        value = self.check_thetas_boundry(value)
        logging.info('KinematicsOps: Converting angle value: %s to pwm value: %s', str(val), str(value))
        return value

    def get_home_angle(self):
        thetas = self.arm_kinematics.get_home_angle()
        logging.info('KinematicsOps: Get home thetas %s ', str(thetas))
        return thetas.copy()

    def get_rand_angle(self, joint_ind):
        min_val = round(self.get_min_angle(joint_ind))
        max_val = round(self.get_max_angle(joint_ind))
        value = random.randint(min(min_val, max_val), max(min_val, max_val))
        logging.info('KinematicsOps: Getting random value: %d for joint number: %d', value, joint_ind)
        return value

    def forward_kinematics(self, thetas):
        logging.info('KinematicsOps: Forware kinematics for thetas = %s', str(thetas))
        thetas, is_collision, H, T = self.arm_kinematics.run_forward_kinematics(self.gripper_pos, thetas)
        logging.warning('KinematicsOps: Estimated pos is %s ', str(T[:3, 3]))
        if self.enable_collision and is_collision:
            logging.warning('KinematicsOps: Collision setting to prev thetas %s', str(self.prev_thetas))
            thetas, is_collision, H, T = self.arm_kinematics.run_forward_kinematics(self.gripper_pos, self.prev_thetas)
            logging.warning('KinematicsOps: Collision after setting is collision: %d', is_collision)
            thetas = self.prev_thetas.copy()
        else:
            self.prev_thetas = thetas.copy()
        return thetas, is_collision, H, T

    def set_collision_state(self, flg):
        logging.info('KinematicsOps: Setting collision state: %d', flg)
        self.enable_collision = flg

    def set_gripper_pos(self, gripper_pos):
        logging.info('KinematicsOps: Setting gripper state: %s', gripper_pos)
        self.gripper_pos = gripper_pos

    def get_gripper_pos(self):
        return self.gripper_pos

    def run_inv_kinematics(self, pos):
        logging.info('KinematicsOps: Run inv kinematics of pos %s ',str(pos))
        if self.gripper_pos == 'None':
            logging.warning('KinematicsOps: Gripper possition state is %s ', self.gripper_pos)
        offset_z, offset_d, offset_a = self.arm_kinematics.get_gripper_parameters(self.gripper_pos)
        theta1, theta2 = self.arm_kinematics.inv_kinematics(pos, offset_z, offset_d, offset_a)
        if len(theta1)>0:
            theta1 = np.append(theta1, 0)
            theta1 = np.append(theta1, 0)
            logging.warning('KinematicsOps: Estimated thetas are %s ', str(theta1))
            return theta1
        else:
            return self.thetas

    def check_thetas_boundry(self, pwm):
        for i in range(len(pwm)):
            pwm[i] = self.check_pwm_boundry(i, pwm[i], self.min_pwm[i], self.max_pwm[i])
        return pwm

    def check_pwm_boundry(self, i, pwm, min_pwm, max_pwm):
        if (pwm < min_pwm):
            logging.error("KinematicsOps, servo %d pwm %d is out of min boundry %d", i, pwm, min_pwm)
            pwm = min_pwm
        if (pwm > max_pwm):
            logging.error("KinematicsOps, servo %d pwm %d is out of max boundry %d", i, pwm, max_pwm)
            pwm = max_pwm
        return pwm