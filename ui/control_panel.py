from ui.sliders_controllers import SlidersController
import tkinter as tk
import logging
# from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class ControlPannel():
    def __init__(self, frame_cp, robot_manager, enable_collision=True):
        self.frame_cp = frame_cp
        self.robot_manager = robot_manager

        self.buttons_width = 15
        self.buttons_height = 3

        self.gripper_pos_list = [
            "None",
            "Home",
            "Vertical",
            "Horizontal",
        ]

        self.run_to_list = [
            "Home",
            "Max",
            "Min",
            "Random",
            "Span",
            "Squeeze",
        ]

        self.run_to_type = tk.StringVar()
        self.run_to_type.set(self.run_to_list[0])
        self.gripper_pos = tk.StringVar()
        self.gripper_pos.set(robot_manager.get_config_gripper_state())
        self.enable_collision = tk.BooleanVar()
        self.enable_collision.set(robot_manager.get_config_collision_flg())
        # self.run = True

        self.cmd_txt = tk.StringVar()
        self.gripper_open_close = tk.BooleanVar()
        self.gripper_open_close.set(False)

        self.slider_creator()
        self.create_plotter_canvas()
        self.create_button()
        # self.create_general_button()
        # self.set_canvas_figure()
        # self.slider_creator()
        # self.cmd_line()

    def create_plotter_canvas(self):
        self.frame_cp.columnconfigure(0, weight=4)
        self.frame_cp.rowconfigure(0, weight=4)
        # self.data_frame = tk.Frame(self.frame_cp, bg='white', highlightbackground="black", highlightthickness=1)
        # self.data_frame.grid(row=0, column=0, rowspan=1, columnspan=1, sticky='nsew')
        thetas = self.sliders_controller.get_values()
        self.figure = self.robot_manager.show_kinematics(thetas)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self.frame_cp)
        # toolbar = NavigationToolbar2Tk(self.figure_canvas, self.data_frame)
        # toolbar.update()
        self.figure_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    # def set_canvas_figure(self):
    #     self.sliders_controller.set_canvas_figure(self.figure_canvas)

    def slider_creator(self):
        self.frame_cp.columnconfigure(0, weight=1)
        self.frame_cp.rowconfigure(1, weight=2)
        self.sliders_frame = tk.Frame(self.frame_cp, highlightbackground="black", highlightthickness=1)
        self.sliders_frame.grid(column=0, row=1, sticky='nsew')
        self.sliders_controller = SlidersController(self.sliders_frame, self.robot_manager)

    def send_cmd_msg(self, event):
        msg = self.cmd_txt.get()
        logging.info('ControlPannel: Send arduino cmd msg %s', msg)
        self.robot_manager.send_arduino_cmd_msg(msg)
        self.cmd_entry.delete(0, 'end')

    # def create_general_button(self):
    #     self.frame_cp.columnconfigure(2, weight=1)
    #     self.frame_cp.rowconfigure(2, weight=1)
    #     self.buttons_frame = tk.Frame(self.frame_cp, highlightbackground="black", highlightthickness=1)
    #     self.buttons_frame.grid(column=2, row=2, sticky='nsew')
    #
    #     # tk.Button(self.buttons_frame, text='Restart', width=self.buttons_width,
    #     #                                height=self.buttons_height, bd='10', command=self.restart).grid(row=0, column=0, sticky='nsew')
    #
    #     tk.Button(self.buttons_frame, text='Stop', width=self.buttons_width,
    #               height=self.buttons_height, bd='10', command=self.stop).grid(row=0, column=1, sticky='nsew')
    #
    #     tk.Button(self.buttons_frame, text='Draw Circle', width=self.buttons_width,
    #               height=self.buttons_height, bd='10', command=self.draw_circle).grid(row=1, column=1, sticky='nsew')

    def create_button(self):
        self.frame_cp.columnconfigure(0, weight=1)
        self.frame_cp.rowconfigure(2, weight=1)
        self.buttons_frame = tk.Frame(self.frame_cp, highlightbackground="black", highlightthickness=1)
        self.buttons_frame.grid(column=0, row=2, sticky='nsew')

        tk.Label(self.buttons_frame, text="Run to").grid(row=0, column=0, sticky='w')
        self.run_to_type.trace("w", self.run_to)
        opt = tk.OptionMenu(self.buttons_frame, self.run_to_type, *self.run_to_list)
        opt.config(width=self.buttons_width)
        opt.config(height=self.buttons_height)
        opt.grid(row=0, column=1, sticky='snew')

        tk.Label(self.buttons_frame, text="Gripper type").grid(row=1, column=0, sticky='w')
        self.gripper_pos.trace("w", self.set_gripper_pos)
        opt = tk.OptionMenu(self.buttons_frame, self.gripper_pos, *self.gripper_pos_list)
        opt.config(width=self.buttons_width)
        opt.config(height=self.buttons_height)
        opt.grid(row=1, column=1, sticky='snew')

        tk.Checkbutton(self.buttons_frame, text='Open Gripper', width=self.buttons_width,
                       height=self.buttons_height, bd='10', command=self.open_close_gripper,
                       variable=self.gripper_open_close, onvalue=True, offvalue=False).grid(row=2, column=0)

        tk.Checkbutton(self.buttons_frame, text='Enable Collision', width=self.buttons_width,
                                         height=self.buttons_height, bd='10', command=self.set_collision_state,
                                         variable=self.enable_collision, onvalue=True, offvalue=False).grid(row=2, column=1)

        # tk.Button(self.buttons_frame, text='Draw Circle', width=self.buttons_width,
        #                                height=self.buttons_height, bd='10', command=self.draw_circle).grid(row=2, column=2, sticky='nsew')

        tk.Label(self.buttons_frame, text='Cmd').grid(row=3, column=0, sticky='snew')
        self.cmd_entry = tk.Entry(self.buttons_frame, width=30, textvariable=self.cmd_txt, takefocus=False)
        self.cmd_entry.bind('<Return>', self.send_cmd_msg)
        self.cmd_entry.grid(row=3, column=1, sticky='snew')

    def run_to(self, *args):
        state = self.run_to_type.get()
        logging.info('ControlPannel: Run to position %s', state)
        if state=='Home':
            self.sliders_controller.set_home_values()
        elif state=='Min':
            self.sliders_controller.set_min_values()
        elif state=='Max':
            self.sliders_controller.set_max_values()
        elif state=='Random':
            self.sliders_controller.set_rand_values()
        elif state=='Squeeze':
            self.sliders_controller.set_squeeze_values()
        elif(state=='Span'):
            self.sliders_controller.set_span_values()

    def set_gripper_pos(self, *args):
        self.robot_manager.set_gripper_pos(self.gripper_pos.get())

    def set_collision_state(self):
        self.robot_manager.set_collision_state(self.enable_collision.get())

    def open_close_gripper(self):
        if self.gripper_open_close.get():
            self.robot_manager.open_gripper()
        else:
            self.robot_manager.close_gripper()

    def set_thetas_to_sliders(self):
        thetas = self.robot_manager.get_thetas()
        self.sliders_controller.set_angle_values(thetas)
        self.figure_canvas.draw()
