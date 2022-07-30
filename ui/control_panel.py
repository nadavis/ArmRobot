from ui.sliders_controllers import SlidersController
import tkinter as tk

class ControlPannel():
    def __init__(self, frame_cp, robot_manager, enable_collision=True):
        self.frame_cp = frame_cp
        self.robot_manager = robot_manager

        self.buttons_width = 15
        self.buttons_height = 5

        self.options_list = [
            "None",
            "Vertical",
            "Horizontal",
        ]

        self.gripper_type = tk.StringVar()
        self.gripper_type.set(robot_manager.get_gripper_state())
        self.enable_collision = tk.BooleanVar()
        self.enable_collision.set(robot_manager.get_collision_flg())

        self.cmd_txt = tk.StringVar()
        self.gripper_open_close = tk.BooleanVar()
        self.gripper_open_close.set(False)

        self.create_plotter_canvas()
        self.create_button()
        self.slider_creator()
        self.cmd_line()

    def create_plotter_canvas(self):
        self.frame_cp.columnconfigure(1, weight=1)
        self.frame_cp.rowconfigure(0, weight=1)
        self.dataCanvas = tk.Canvas(self.frame_cp, bg='white')
        self.dataCanvas.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW)

        # vsb = tk.Scrollbar(self.frame_cp, orient='vertical', command=self.dataCanvas.yview)
        # vsb.grid(row=0, column=2, rowspan=3, sticky=tk.NS)
        #
        # self.dataCanvas.config(yscrollcommand=vsb.set, scrollregion=self.dataCanvas.bbox('all'))
        # self.dataCanvas.yview_moveto('1.0')
        #
        # self.dataFrame = tk.Frame(self.dataCanvas, bg='black')
        # self.dataCanvas.create_window((10, 0), window=self.dataFrame, anchor='nw')

    def slider_creator(self):
        self.frame_cp.columnconfigure(0, weight=1)
        self.frame_cp.rowconfigure(0, weight=1)
        self.sliders_frame = tk.Frame(self.frame_cp)
        self.sliders_frame.grid(column=0, row=0, sticky=tk.EW)
        self.sliders_controller = SlidersController(self.sliders_frame, self.robot_manager)

    def send_cmd_msg(self, event):
        msg = self.cmd_txt.get()
        print(msg)
        # self.arduino_msg.sendToArduino(msg)
        self.cmd_entry.delete(0, 'end')

    def cmd_line(self):
        self.frame_cp.columnconfigure(0, weight=1)
        self.frame_cp.rowconfigure(2, weight=1)
        self.cmd_frame = tk.Frame(self.frame_cp)
        self.cmd_frame.grid(column=0, row=2)
        tk.Label(self.cmd_frame, text='Cmd').grid(row=0, column=0, sticky='ns')
        self.cmd_entry = tk.Entry(self.cmd_frame, width=40, textvariable=self.cmd_txt, takefocus=False)
        self.cmd_entry.bind('<Return>', self.send_cmd_msg)
        self.cmd_entry.grid(row=0, column=1, sticky='ns')

    def create_button(self):
        self.frame_cp.columnconfigure(0, weight=1)
        self.frame_cp.rowconfigure(1, weight=1)
        self.buttons_frame = tk.Frame(self.frame_cp)
        self.buttons_frame.grid(column=0, row=1)

        rndButton = tk.Button(self.buttons_frame, text='Random', width=self.buttons_width,
                              height=self.buttons_height, bd='10', command=self.run_random).grid(row=0, column=0, sticky='ns')

        spanButton = tk.Button(self.buttons_frame, text='Span', width=self.buttons_width,
                               height=self.buttons_height, bd='10', command=self.run_span).grid(row=1, column=0, sticky='ns')

        homeButton = tk.Button(self.buttons_frame, text='Home', width=self.buttons_width,
                               height=self.buttons_height, bd='10', command=self.run_home).grid(row=0, column=1, sticky='ns')

        squeezeButton = tk.Button(self.buttons_frame, text='Squeeze', width=self.buttons_width,
                                  height=self.buttons_height, bd='10', command=self.run_squeeze).grid(row=1, column=1, sticky='ns')

        spanButton = tk.Button(self.buttons_frame, text='Min', width=self.buttons_width,
                               height=self.buttons_height, bd='10', command=self.run_min).grid(row=1, column=2, sticky='ns')

        homeButton = tk.Button(self.buttons_frame, text='Max', width=self.buttons_width,
                               height=self.buttons_height, bd='10', command=self.run_max).grid(row=0, column=2, sticky='ns')

        gripperOpenButton = tk.Checkbutton(self.buttons_frame, text='Open Gripper', width=self.buttons_width,
                                         height=self.buttons_height, bd='10', command=self.open_close_gripper,
                                            variable=self.gripper_open_close, onvalue=True, offvalue=False).grid(row=1, column=3, sticky='ns')

        gripperCloseButton = tk.Button(self.buttons_frame, text='Draw Circle', width=self.buttons_width,
                                       height=self.buttons_height, bd='10', command=self.draw_circle).grid(row=0, column=3, sticky='ns')


        collisionButton = tk.Checkbutton(self.buttons_frame, text='Enable Collision', width=self.buttons_width,
                                         height=self.buttons_height, bd='10', command=self.set_collision_state,
                                         variable=self.enable_collision, onvalue=True, offvalue=False).grid(row=0, column=4, sticky='ns')

        self.gripper_type.trace("w", self.set_gripper_type)
        opt = tk.OptionMenu(self.buttons_frame, self.gripper_type, *self.options_list).grid(row=1, column=4, sticky='ns')

    def run_random(self):
        self.sliders_controller.set_rand_values()

    def run_span(self):
        self.sliders_controller.set_span_values()

    def run_home(self):
        self.sliders_controller.set_home_values()

    def run_squeeze(self):
        self.sliders_controller.set_squeeze_values()

    def set_gripper_type(self, *args):
        self.robot_manager.set_gripper_type(self.gripper_type.get())

    def set_collision_state(self):
        self.robot_manager.set_collision_state(self.enable_collision.get())

    def open_close_gripper(self):
        if self.gripper_open_close.get():
            self.sliders_controller.open_gripper()
        else:
            self.sliders_controller.close_gripper()

    def draw_circle(self):
        self.sliders_controller.draw_circle()

    def run_min(self):
        self.sliders_controller.set_min_values()

    def run_max(self):
        self.sliders_controller.set_max_values()
