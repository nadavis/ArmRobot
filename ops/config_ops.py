import logging

import yaml

class ConfigOps():
    def __init__(self):
        config = []
        try:
            with open("config/config.yml", 'r') as conf_file:
                self.config = yaml.load(conf_file, Loader=yaml.FullLoader)
        except:
            logging.error("Can not open configuration")
            exit()

        self.arduino_config = self.config['arduino']
        self.servo_config = self.config['servo_spec']
        self.video_stream_config = self.config['video_stream']
        self.kinematics_config = self.config['kinematics']
        self.cv_config = self.config['obj_detection']
