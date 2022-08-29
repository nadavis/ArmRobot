import logging

import yaml

class ConfigOps():
    def __init__(self, path="config/config.yml"):
        try:
            with open(path, 'r') as conf_file:
                self.config = yaml.load(conf_file, Loader=yaml.FullLoader)
        except:
            logging.error("ConfigOps: Can not open configuration")
            exit()

        self.arduino_config = self.config['arduino']
        self.servo_config = self.config['servo_spec']
        self.video_stream_config = self.config['video_stream']
        self.kinematics_config = self.config['kinematics']
        self.cv_config = self.config['obj_detection']

    def get_fps(self):
        return self.video_stream_config['fps']

    def get_camera_id(self):
        return self.video_stream_config['camera_id']

    def get_width_target(self):
        return self.video_stream_config['width_target']

    def get_angle_max(self):
        return self.servo_config['angle_max']

    def get_pwm_max(self):
        return self.servo_config['pwm_max']

    def get_servo_gear_ratio(self):
        return self.servo_config['gear_ratio']

    def get_pwm_min(self):
        return self.servo_config['pwm_min']

    def get_servo_home(self):
        return self.servo_config['home']

    def get_servo_min(self):
        return self.servo_config['min']

    def get_servo_max(self):
        return self.servo_config['max']

    def get_servo_direction(self):
        return self.servo_config['servo_direction']

    def get_links_size(self):
        return self.kinematics_config['link_size']

    def get_enable_collision_state(self):
        return self.kinematics_config['enable_collision']

    def get_gripper_state(self):
        return self.kinematics_config['gripper_state']

    def get_thetas_zero(self):
        return self.kinematics_config['theta0']

    def get_home_pwm(self):
        return self.servo_config['home']

    def get_z_limit(self):
        return self.kinematics_config['z_limit']

    def get_msg_buff(self):
        return self.arduino_config['msg_buff']

    def get_arduino_sleep_msg(self):
        return self.arduino_config['sleep_msg']

    def get_arduino_port(self):
        return self.arduino_config['port'] #'/dev/cu.usbmodem141201'

    def get_arduino_time_msg_interval(self):
        return self.arduino_config['time_msg_interval']

    def get_min_obj_size(self):
        return self.cv_config['min_obj_size']