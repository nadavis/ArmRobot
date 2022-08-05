import logging
from arduino.arduino_msg import ArduinoMsg

class ArduinoMsgOps:
    def __init__(self, config_ops):
        time_msg_interval = config_ops.get_arduino_time_msg_interval()
        msg_buff = config_ops.get_msg_buff()
        sleep_msg = config_ops.get_arduino_sleep_msg()
        port = config_ops.get_arduino_port()

        self.arduino_msg = ArduinoMsg(msg_buff, port, time_msg_interval, sleep_msg)
        servo_min = config_ops.get_servo_min()
        servo_max = config_ops.get_servo_max()
        self.gripper_ind = len(servo_max)-1
        self.open_gripper_pwm = servo_max[self.gripper_ind]
        self.close_gripper_pwm = servo_min[self.gripper_ind]

    def send_kinematic_pwm(self, ind, pwm):
            msg = ('run:' + str(ind) + ':' + str(round(pwm)))
            self.arduino_msg.send_to_arduino(msg)
        # print('lock gripper msg: ', [self.current_value.get(), self.kinematics.theta[self.grid_column_pos]])
        # print('lock gripper pwm msg: ', [len(self.kinematics.theta0), self.kinematics.pwm[self.grid_column_pos]])
        # self.send_msg_pwm(self.grid_column_pos, self.kinematics.pwm[self.grid_column_pos])
        # if (self.get_gripper_state() != 'None'):
        #     print('lock gripper msg: ', [self.kinematics.theta[3], self.kinematics.theta[4]])
        #     print('lock gripper pwm msg: ', [self.kinematics.pwm[3], self.kinematics.pwm[4]])
        #     self.send_msg_pwm(3, self.kinematics.pwm[3])
        #     self.send_msg_pwm(4, self.kinematics.pwm[4])

    def open_gripper(self):
        logging.info('ArduinoMsgOps: Gripper is opening')
        self.send_kinematic_pwm(self.gripper_ind, self.open_gripper_pwm)

    def close_gripper(self):
        logging.info('ArduinoMsgOps: Gripper is closing')
        self.send_kinematic_pwm(self.gripper_ind, self.close_gripper_pwm)

    def get_servo_min(self):
        return self.servo_config['min']

    def get_servo_max(self):
        return self.servo_config['max']