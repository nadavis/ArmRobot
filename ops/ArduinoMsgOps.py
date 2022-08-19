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

    def get_arduino_msg(self):
        msg = self.arduino_msg.check_serial_port()
        # logging.info('ArduinoMsgOps: Get arduino msg %s', msg)

    def send_cmd_msg(self, msg):
        self.arduino_msg.send_to_arduino(msg)

    def send_kinematic_pwm(self, pwm_vect):
        msg = 'run'
        for pwm in pwm_vect:
            msg += ':' + str(round(pwm))
        logging.info('ArduinoMsgOps: Send msg %s to arduino', msg)
        self.arduino_msg.send_to_arduino(msg)

    def open_gripper(self):
        logging.info('ArduinoMsgOps: Gripper is opening')
        # self.send_kinematic_pwm(self.gripper_ind, self.open_gripper_pwm)
        msg = 'gripper:' + str(self.open_gripper_pwm)
        self.arduino_msg.send_to_arduino(msg)

    def close_gripper(self):
        logging.info('ArduinoMsgOps: Gripper is closing')
        # self.send_kinematic_pwm(self.gripper_ind, self.close_gripper_pwm)
        msg = 'gripper:' + str(self.close_gripper_pwm)
        self.arduino_msg.send_to_arduino(msg)

    def get_servo_min(self):
        return self.servo_config['min']

    def get_servo_max(self):
        return self.servo_config['max']