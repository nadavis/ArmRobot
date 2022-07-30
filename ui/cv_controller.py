import tkinter as tk
from PIL import Image
from PIL import ImageTk
import numpy as np

class CVController():
    def __init__(self, frame_od, robot_manager):
        self.frame_od = frame_od
        self.robot_manager = robot_manager
        self.resize_dim = self.robot_manager.get_video_size()
        # self.control_panel = control_panel
        # self.config = config
        self.buttons_width = 15
        self.buttons_height = 5
        self.x = tk.IntVar()
        self.x.set(-30)
        self.y = tk.IntVar()
        self.y.set(30)
        self.z = tk.IntVar()
        self.z.set(-3)
        self.obj_list = [
            "None",
            "RedBox",
        ]
        self.target_obj = tk.StringVar(self.frame_od)
        self.target_obj.set(self.obj_list[0])

        self.create_button()
        self.create_video_canvas()
        self.create_entry()

    def go_to(self):
        print('go to')

    def get_frame(self):
        frame, red_only = self.robot_manager.get_frame(True)
        self.frame = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.video_canvas.create_image(0, 0, image=self.frame, anchor=tk.NW)
        self.red_only = ImageTk.PhotoImage(image=Image.fromarray(red_only))
        self.signal_canvas.create_image(0, 0, image=self.red_only, anchor=tk.NW)

    def save_background(self):
        print('Save background')
        self.background = self.robot_manager.set_background(True)
        self.image = ImageTk.PhotoImage(image=Image.fromarray(self.background))
        self.background_canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def find_obj(self, *args):
        print('Find obj: ', self.target_obj.get())

    def clear_data(self):
        print('Clear data')

    def create_video_canvas(self):
        self.frame_od.columnconfigure(0, weight=1)
        self.frame_od.rowconfigure(0, weight=1)
        # print(self.video_stream.width)
        self.video_canvas = tk.Canvas(self.frame_od, width = self.resize_dim[0], height = self.resize_dim[1])
        self.video_canvas.grid(row=0, column=0, sticky=tk.NW)

        self.background_canvas = tk.Canvas(self.frame_od, width = self.resize_dim[0], height = self.resize_dim[1])
        self.background_canvas.grid(row=0, column=2, sticky=tk.NW)

        self.signal_canvas = tk.Canvas(self.frame_od, width = self.resize_dim[0], height = self.resize_dim[1])
        self.signal_canvas.grid(row=0, column=1, sticky=tk.NW)

        self.diff_canvas = tk.Canvas(self.frame_od, width=self.resize_dim[0],
                                      height=self.resize_dim[1])
        self.diff_canvas.grid(row=1, column=2, sticky=tk.NW)

    def create_button(self):
        self.frame_od.columnconfigure(0, weight=1)
        self.frame_od.rowconfigure(1, weight=1)
        self.buttons_frame = tk.Frame(self.frame_od)
        self.buttons_frame.grid(column=0, row=1)

        objButton = tk.Button(self.buttons_frame, text='go to', width=self.buttons_width, height=self.buttons_height, bd='10', command=self.go_to)
        objButton.grid(row=0, column=0, sticky='ns')

        bgButton = tk.Button(self.buttons_frame, text='save bkg', width=self.buttons_width, height=self.buttons_height, bd='10', command=self.save_background)
        bgButton.grid(row=0, column=1, sticky='ns')

        calButton = tk.Button(self.buttons_frame, text='store data', width=self.buttons_width, height=self.buttons_height,
                             bd='10', command=self.store_data)
        calButton.grid(row=0, column=2, sticky='ns')

        clearButton = tk.Button(self.buttons_frame, text='clear data', width=self.buttons_width,
                              height=self.buttons_height,
                              bd='10', command=self.clear_data)
        clearButton.grid(row=1, column=0, sticky='ns')

        genButton = tk.Button(self.buttons_frame, text='rand data', width=self.buttons_width,
                                height=self.buttons_height,
                                bd='10', command=self.generate_rand_xyz)
        genButton.grid(row=1, column=1, sticky='ns')

        self.target_obj.trace("w", self.find_obj)
        opt = tk.OptionMenu(self.buttons_frame, self.target_obj, *self.obj_list)
        opt.grid(row=0, column=3, sticky='ns')

    def set_xyz(self, msg):
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]
        print('Coord: ', self.world_coord)

    def generate_rand_xyz(self):
        self.x.set(np.random.randint(-40, 40, size=1)[0])
        self.y.set(np.random.randint(-40, -10, size=1)[0])
        self.z.set(3)
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]
        print('Coord: ', self.world_coord)

    def store_data(self):
        print('Store data')

    def create_entry(self):
        self.frame_od.columnconfigure(0, weight=1)
        self.frame_od.rowconfigure(2, weight=1)
        self.entry_frame = tk.Frame(self.frame_od)
        self.entry_frame.grid(column=0, row=2)

        tk.Label(self.entry_frame, text="x").grid(row=0)
        tk.Label(self.entry_frame, text="y").grid(row=1)
        tk.Label(self.entry_frame, text="z").grid(row=2)


        self.xEntry = tk.Entry(self.entry_frame, textvariable=self.x, width=self.buttons_width, bd='2')
        self.xEntry.bind('<Return>', self.set_xyz)
        self.xEntry.grid(row=0, column=1, sticky='ns')

        self.yEntry = tk.Entry(self.entry_frame, textvariable=self.y, width=self.buttons_width, bd='2')
        self.yEntry.bind('<Return>', self.set_xyz)
        self.yEntry.grid(row=1, column=1, sticky='ns')

        self.zEntry = tk.Entry(self.entry_frame, textvariable=self.z, width=self.buttons_width, bd='2')
        self.zEntry.bind('<Return>', self.set_xyz)
        self.zEntry.grid(row=2, column=1, sticky='ns')