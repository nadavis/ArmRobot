import tkinter as tk
import logging

class SliderFrame:
    def __init__(self, slider_number, container, robot_manager):
        # #self.gripper_locked = False
        # self.gripper_locked = 'None'
        # self.enable_collision = False
        # self.plot_tools = plot_tools
        # self.kinematics = kinematics
        # self.current_value = tk.IntVar()
        # self.current_value.set(0)
        # self.last_value = self.current_value.get()
        # self.container = container
        # self.arduino_msg = arduino_msg
        # self.grid_column_pos = grid_column_pos
        # self.grid_row_pos = grid_row_pos
        # self.min_motor_val = min_motor_val
        # self.max_motor_val = max_motor_val
        # self.home_motor_val = home_motor_val
        # self.motor_name = motor_name
        # self.servo_direction = servo_direction
        # self.pwm2angel = pwm2angel
        #
        # # self.min_motor_angel = self.kinematics.pwm_2_angel(grid_column_pos, min_motor_val)
        # # self.max_motor_angel = self.kinematics.pwm_2_angel(grid_column_pos, max_motor_val)
        # # self.home_motor_angel = self.kinematics.pwm_2_angel(grid_column_pos, home_motor_val)
        # self.min_motor_angel = self.pwm_2_angel(min_motor_val)
        # self.max_motor_angel = self.pwm_2_angel(max_motor_val)
        # self.home_motor_angel = self.pwm_2_angel(home_motor_val)

        self.name = 'Joint' + str(slider_number + 1)
        self.container = container
        self.robot_manager = robot_manager
        self.slider_number = slider_number
        self.current_value = tk.IntVar()
        self.current_value.set(0)

        self.container.columnconfigure(slider_number, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.frame = tk.Frame(self.container)
        self.frame.grid(column=slider_number, row=0)

        self.create_slider_params()

    def create_slider_params(self):
        self.joint_slider_label = tk.Label(self.frame, text=self.name)
        self.joint_slider_label.grid(column=0, row=0)
        min_motor_angle = self.robot_manager.get_min_angle(self.slider_number)
        max_motor_angle = self.robot_manager.get_max_angle(self.slider_number)
        if(self.robot_manager.get_joint_direction(self.slider_number)==1):
            self.joint_slider = tk.Scale(self.frame, from_=min_motor_angle, to=max_motor_angle, orient='vertical',
                                     command=self.slider_changed,
                                     variable=self.current_value, length=200, takefocus=False)
        else:
            self.joint_slider = tk.Scale(self.frame, from_=-max_motor_angle,
                                         to=-min_motor_angle, orient='vertical',
                                         command=self.slider_changed,
                                         variable=self.current_value, length=200, takefocus=False)

        self.joint_slider.grid(column=0, row=1, columnspan=2)

    def set_value(self, value):
        self.joint_slider.set(value)

    def set_home_value(self):
        self.set_value(0)

    def set_rand_value(self):
        value = self.robot_manager.get_rand_angle(self.slider_number)
        self.set_value(value)

    def set_min_value(self):
        self.set_value(self.robot_manager.get_min_angle(self.slider_number))

    def set_max_value(self):
        self.set_value(self.robot_manager.get_max_angle(self.slider_number))

    def slider_changed(self, event):
        logging.info('Slider number %d is changing', self.slider_number)
        self.robot_manager.set_current_angle(self.slider_number, self.current_value.get())

    # def slider_changed(self, event):
    #     logging.info('Slider number: ', self.slider_number,' is changing')
    #
    #     theta = self.kinematics.set_theta_by_motor_ind(self.grid_column_pos, self.current_value.get())
    #     theta, pos, is_collision, H, T = self.kinematics.run_forward_kinematics()
    #     self.plot_tools.show_kinematics(theta, H, T)
    #     if not is_collision:
    #         # print("--- SEND MSG---")
    #         # print('ind:', self.grid_column_pos)
    #         # print('theta: ', theta)
    #         # print('pwm: ', self.kinematics.pwm)
    #         # print('pos: ', pos)
    #         self.send_kinematic_angel()
    #         if (self.grid_column_pos < len(self.kinematics.theta0)):
    #             self.set_value(theta[self.grid_column_pos])
    #
    # def get_slider_angel(self):
    #     return self.current_value.get()
    #
    # def send_kinematic_angel(self):
    #     if(self.grid_column_pos<len(self.kinematics.theta0)):
    #         print('lock gripper msg: ', [self.current_value.get(), self.kinematics.theta[self.grid_column_pos]])
    #         print('lock gripper pwm msg: ', [len(self.kinematics.theta0), self.kinematics.pwm[self.grid_column_pos]])
    #         self.send_msg_pwm(self.grid_column_pos, self.kinematics.pwm[self.grid_column_pos])
    #         if (self.gripper_locked != 'None'):
    #             print('lock gripper msg: ', [self.kinematics.theta[3], self.kinematics.theta[4]])
    #             print('lock gripper pwm msg: ', [self.kinematics.pwm[3], self.kinematics.pwm[4]])
    #             self.send_msg_pwm(3, self.kinematics.pwm[3])
    #             self.send_msg_pwm(4, self.kinematics.pwm[4])
    #     else:
    #         self.send_msg_angel(self.grid_column_pos, self.current_value.get())
    #
    # def send_msg_angel(self, ind, val):
    #     self.arduino_msg.send_msg_by_values(ind, self.angel_2_pwm(val))
    #
    # def send_msg_pwm(self, ind, val):
    #     self.arduino_msg.send_msg_by_values(ind, val)

class SlidersController:
    def __init__(self, sliders_frame, robot_manager):
        self.joint_slider = []
        self.robot_manager = robot_manager
        self.num_of_joint = robot_manager.get_num_of_joints()
        for i in range(0, self.num_of_joint):
            name = 'Joint' + str(i+1)
            slider = SliderFrame(i, sliders_frame, robot_manager)
            self.joint_slider.append(slider)

    # def set_values(self, values):
    #     for i in range(0, self.num_of_joint):
    #         # print(values[i])
    #         self.joint_slider[i].set_value(values[i])

    # def set_collision_state(self, flg):
    #     self.robot_manager.set_collision_state(flg)
    #     # self.kinematics.set_avoid_collision(flg)
    #     # for i in range(0, self.num_of_joint):
    #     #     self.joint_slider[i].enable_collision = flg
    #
    # def set_gripper_type(self, flg):
    #     self.gripper_locked = flg
    #     # self.kinematics.set_gripper_locked(flg)
    #     for i in range(0, self.num_of_joint):
    #         self.joint_slider[i].gripper_locked = flg

    def set_home_values(self):
        # self.sliders_set_lock_gripper(False)
        # self.sliders_set_collision_flg(True)
        # self.kinematics.go_home()
        for i in range(0, self.num_of_joint):
            self.joint_slider[i].set_home_value()

    def set_min_values(self):
        self.joint_slider[0].set_home_value()
        for i in range(1, self.num_of_joint):
            self.joint_slider[i].set_min_value()

    def set_max_values(self):
        self.joint_slider[0].set_home_value()
        for i in range(1, self.num_of_joint):
            self.joint_slider[i].set_max_value()

    def set_span_values(self):
        self.joint_slider[0].set_home_value()
        self.joint_slider[1].set_value(90)
        self.joint_slider[2].set_home_value()
        self.joint_slider[3].set_home_value()
        self.joint_slider[4].set_home_value()

    def open_gripper(self):
        self.robot_manager.open_gripper()

    def close_gripper(self):
        self.robot_manager.close_gripper()

    def set_squeeze_values(self):
        self.joint_slider[0].set_home_value()
        self.joint_slider[1].set_min_value()
        self.joint_slider[2].set_max_value()
        self.joint_slider[3].set_home_value()
        self.joint_slider[4].set_min_value()

    def set_rand_values(self):
        for i in range(0, self.num_of_joint):
            self.joint_slider[i].set_rand_value()
        # self.show_self_kinematics()

    # def send_msg(self, theta):
    #     for i in range(0, self.num_of_joint-1):
    #         self.joint_slider[i].send_msg_angel(i, theta[i])

    def show_values(self):
        for i in range(0, self.num_of_joint):
            print('Joint value ' + str(i) + ':' + str(self.joint_slider[i].current_value.get()))

    def draw_circle(self):
        coords = []
        thetas = []
        # return coords, thetas