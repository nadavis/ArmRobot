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

        self.arm_kinematics = ArmKinematics(config_manager.kinematics_config,
                                       config_manager.servo_config)

        self.arduino_msg = ArduinoMsg(config_manager.arduino_config['msg_buff'],
                                 config_manager.arduino_config['port'],
                                 config_manager.arduino_config['time_msg_interval'],
                                 config_manager.arduino_config['sleep_msg'])

        self.max_angle_motor_spec = np.array(config_manager.servo_config['angel_max'])
        self.max_motor_spec = np.array(config_manager.servo_config['pwm_max'])
        self.gear_spec = np.array(config_manager.servo_config['gear_ratio'])
        self.min_motor_spec = np.array(config_manager.servo_config['pwm_min'])
        self.pwm2angle = self.max_angle_motor_spec / (self.gear_spec * (self.max_motor_spec - self.min_motor_spec))
        self.home_pwm = np.array(config_manager.servo_config['home'])
        self.min_pwm = np.array(config_manager.servo_config['min'])
        self.max_pwm = np.array(config_manager.servo_config['max'])
        self.servo_direction = np.array(config_manager.servo_config['servo_direction'])

    def get_num_of_joints(self):
        logging.info('Getting number of dof, number of dof is: %d', self.arm_kinematics.num_of_dof)
        return self.arm_kinematics.num_of_dof

    def get_joint_direction(self, joint_ind):
        value = self.servo_direction[joint_ind]
        logging.info('Getting direction joint is: %d for joint number: %d', value, joint_ind)
        return value

    def get_min_angle(self, joint_ind):
        value = self.pwm_2_angle(joint_ind, self.min_pwm)
        logging.info('Getting min value: %.4f for joint number: %d', value, joint_ind)
        return value

    def get_max_angle(self, joint_ind):
        value = self.pwm_2_angle(joint_ind, self.max_pwm)
        logging.info('Getting max value: %.4f for joint number: %d', value, joint_ind)
        return value

    def pwm_2_angle(self, ind, val):
        value = (val[ind]-self.home_pwm[ind])*self.pwm2angle[ind]
        logging.info('Converting, PWM value: %d to angle value: %.4f for joint number: %d', val[ind], value, ind)
        return value

    def angle_2_pwm(self, ind, val):
        val = val[ind] * self.servo_direction[ind]
        value = self.home_pwm[ind]+val/self.pwm2angle[ind]
        logging.info('Converting angle value: %.4f to pwm value: %d for joint number: %d', val[ind], value, ind)
        return value

    def get_rand_angle(self, joint_ind):
        min_val = round(self.get_min_angle(joint_ind))
        max_val = round(self.get_max_angle(joint_ind))
        value = random.randint(min(min_val, max_val), max(min_val, max_val))
        logging.info('Getting random value: %d for joint number: %d', value, joint_ind)
        return value

    def set_current_angle(self, joint_ind, value):
        logging.info('Setting value: %d for slider number: %d', value, joint_ind)
        # theta = self.kinematics.set_theta_by_motor_ind(self.grid_column_pos, self.current_value.get())
        # theta, pos, is_collision, H, T = self.kinematics.run_forward_kinematics()
        # self.plot_tools.show_kinematics(theta, H, T)
        # if not is_collision:
        #     # print("--- SEND MSG---")
        #     # print('ind:', self.grid_column_pos)
        #     # print('theta: ', theta)
        #     # print('pwm: ', self.kinematics.pwm)
        #     # print('pos: ', pos)
        #     self.send_kinematic_angel()
        #     if (self.grid_column_pos < len(self.kinematics.theta0)):
        #         self.set_value(theta[self.grid_column_pos])

    def set_collision_state(self, flg):
        logging.info('Setting collision state: %d', flg)
        # return self.kinematics_ops.set_collision_state(flg)

    def set_gripper_type(self, type):
        logging.info('Setting gripper type: %s', type)

    def open_gripper(self):
        logging.info('Opening gripper')

    def close_gripper(self):
        logging.info('OpeninClosingg gripper')