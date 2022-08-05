import tkinter as tk
import logging

class SliderFrame:
    def __init__(self, slider_number, container, robot_manager):
        self.name = 'Joint' + str(slider_number + 1)
        self.container = container
        self.robot_manager = robot_manager
        self.slider_number = slider_number
        self.current_value = tk.IntVar()
        self.current_value.set(0)

        self.container.columnconfigure(slider_number, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.frame = tk.Frame(self.container, highlightbackground="black", highlightthickness=1)
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
                                     variable=self.current_value, takefocus=False)
        else:
            self.joint_slider = tk.Scale(self.frame, from_=-max_motor_angle,
                                         to=-min_motor_angle, orient='vertical',
                                         command=self.slider_changed,
                                         variable=self.current_value, takefocus=False, length=None)

        self.joint_slider.grid(column=0, row=1, sticky='snew')

    def set_value(self, value):
        self.joint_slider.set(value)

    def get_value(self):
        return self.joint_slider.get()

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
        logging.info('SliderFrame: Slider number %d is changing', self.slider_number)
        self.robot_manager.set_current_angle(self.slider_number, self.current_value.get())
        # thetas = self.robot_manager.send_current_angle()
        # self.figure_canvas.draw()
        # self.set_value(thetas[self.slider_number])

    # def set_canvas_figure(self, figure_canvas):
    #     self.figure_canvas = figure_canvas

class SlidersController:
    def __init__(self, sliders_frame, robot_manager):
        self.joint_slider = []
        self.robot_manager = robot_manager
        self.num_of_joint = robot_manager.get_num_of_joints()
        for i in range(0, self.num_of_joint):
            name = 'Joint' + str(i+1)
            slider = SliderFrame(i, sliders_frame, robot_manager)
            self.joint_slider.append(slider)

    def set_home_values(self):
        for i in range(0, self.num_of_joint):
            self.joint_slider[i].set_home_value()

    def get_values(self):
        thetas = []
        for i in range(0, self.num_of_joint):
            thetas.append(self.joint_slider[i].get_value())

        return thetas

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

    def set_squeeze_values(self):
        self.joint_slider[0].set_home_value()
        self.joint_slider[1].set_min_value()
        self.joint_slider[2].set_max_value()
        self.joint_slider[3].set_home_value()
        self.joint_slider[4].set_min_value()

    def set_rand_values(self):
        for i in range(0, self.num_of_joint):
            self.joint_slider[i].set_rand_value()

    def set_angle_values(self, angle):
        for i in range(0, self.num_of_joint):
            self.joint_slider[i].set_value(angle[i])

    def show_values(self):
        for i in range(0, self.num_of_joint):
            logging.info('SliderFrame: Joint value ind %d , value %d', i, self.joint_slider[i].current_value.get())

    # def set_canvas_figure(self, figure_canvas):
    #     for i in range(0, self.num_of_joint):
    #         self.joint_slider[i].set_canvas_figure(figure_canvas)