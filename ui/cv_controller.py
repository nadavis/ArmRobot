import tkinter as tk
from PIL import Image
from PIL import ImageTk
import numpy as np
import cv2 as cv
import logging

class CVController():
    def __init__(self, frame_od, robot_manager):
        self.frame_od = frame_od
        self.robot_manager = robot_manager
        self.resize_dim = self.robot_manager.get_video_size()
        self.buttons_width = 15
        self.buttons_height = 3
        self.x = tk.IntVar()
        self.x.set(-25)
        self.y = tk.IntVar()
        self.y.set(0)
        self.z = tk.IntVar()
        self.z.set(4)
        self.rx = tk.IntVar()
        self.rx.set(8)
        self.ry = tk.IntVar()
        self.ry.set(16)
        self.num_of_sample = tk.IntVar()
        self.num_of_sample.set(15)
        self.obj_list = [
            "None",
            "RedBox",
        ]
        self.target_obj = tk.StringVar(self.frame_od)
        self.target_obj.set(self.obj_list[0])

        self.create_button()
        self.create_video_canvas()
        self.robot_manager.set_target_obj(self.target_obj.get())
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]

        self.run = True
        self.create_general_button()

    def create_video_canvas(self):
        self.frame_od.columnconfigure(1, weight=1)
        self.frame_od.rowconfigure(0, weight=4)
        self.video_canvas = tk.Canvas(self.frame_od, width = self.resize_dim[0], height = self.resize_dim[1], highlightbackground="black", highlightthickness=1)
        self.video_canvas.grid(row=0, column=1, sticky='nswe')

        self.frame_od.columnconfigure(1, weight=1)
        self.frame_od.rowconfigure(1, weight=4)
        self.signal_canvas = tk.Canvas(self.frame_od, width=self.resize_dim[0], height=self.resize_dim[1], highlightbackground="black", highlightthickness=1)
        self.signal_canvas.grid(row=1, column=1, sticky='nswe')

        self.frame_od.columnconfigure(2, weight=1)
        self.frame_od.rowconfigure(0, weight=4)
        self.background_canvas = tk.Canvas(self.frame_od, width = self.resize_dim[0], height = self.resize_dim[1], highlightbackground="black", highlightthickness=1)
        self.background_canvas.grid(row=0, column=2, sticky='nswe')

    def create_button(self):
        self.frame_od.columnconfigure(1, weight=1)
        self.frame_od.rowconfigure(2, weight=1)
        self.buttons_frame = tk.Frame(self.frame_od, highlightbackground="black", highlightthickness=1)
        self.buttons_frame.grid(column=1, row=2, sticky='nswe')

        tk.Button(self.buttons_frame, text='Go to', bd='10', command=self.go_to, width=self.buttons_width, height=self.buttons_height).grid(row=1, column=0, sticky='nsew')

        tk.Button(self.buttons_frame, text='Save bkg', bd='10', command=self.save_background, width=self.buttons_width, height=self.buttons_height).grid(row=0, column=0, sticky='nsew')


        clearButton = tk.Button(self.buttons_frame, text='clear data',
                              bd='10', command=self.clear_data, width=self.buttons_width, height=self.buttons_height)
        clearButton.grid(row=0, column=1, sticky='nsew')

        genButton = tk.Button(self.buttons_frame, text='rand data',
                                bd='10', command=self.generate_rand_xyz, width=self.buttons_width, height=self.buttons_height)
        genButton.grid(row=1, column=1, sticky='nsew')

        tk.Label(self.buttons_frame, text="Object type").grid(row=2, column=0, sticky='snew')
        self.target_obj.trace("w", self.set_target_obj)
        opt = tk.OptionMenu(self.buttons_frame, self.target_obj, *self.obj_list)
        opt.config(width=self.buttons_width)
        opt.config(height=self.buttons_height)
        opt.grid(row=2, column=1, sticky='nsew')

        tk.Button(self.buttons_frame, text='Stop', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.stop).grid(row=0, column=2, sticky='nsew')

        tk.Button(self.buttons_frame, text='Draw Circle', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.draw_circle).grid(row=2, column=2, sticky='nsew')

        tk.Button(self.buttons_frame, text='Save data', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.save_data).grid(row=1, column=2, sticky='nsew')

    def create_general_button(self):
        self.frame_od.columnconfigure(2, weight=1)
        self.frame_od.rowconfigure(2, weight=1)
        self.buttons_general_frame = tk.Frame(self.frame_od, highlightbackground="black", highlightthickness=1)
        self.buttons_general_frame.grid(column=2, row=2, sticky='nsew')


        tk.Label(self.buttons_general_frame, text="x").grid(row=0, column=0, sticky='nsew')
        tk.Label(self.buttons_general_frame, text="y").grid(row=1, column=0, sticky='nsew')
        tk.Label(self.buttons_general_frame, text="z").grid(row=2, column=0, sticky='nsew')
        tk.Label(self.buttons_general_frame, text="rx").grid(row=0, column=2, sticky='nsew')
        tk.Label(self.buttons_general_frame, text="ry").grid(row=1, column=2, sticky='nsew')
        tk.Label(self.buttons_general_frame, text="s").grid(row=2, column=2, sticky='nsew')


        self.xEntry = tk.Entry(self.buttons_general_frame, textvariable=self.x, width=self.buttons_width, bd='2')
        self.xEntry.bind('<KeyRelease>', self.set_xyz)
        self.xEntry.grid(row=0, column=1, sticky='ns')

        self.yEntry = tk.Entry(self.buttons_general_frame, textvariable=self.y, width=self.buttons_width, bd='2')
        self.yEntry.bind('<KeyRelease>', self.set_xyz)
        self.yEntry.grid(row=1, column=1, sticky='nsew')

        self.zEntry = tk.Entry(self.buttons_general_frame, textvariable=self.z, width=self.buttons_width, bd='2')
        self.zEntry.bind('<KeyRelease>', self.set_xyz)
        self.zEntry.grid(row=2, column=1, sticky='nsew')

        self.xEntry = tk.Entry(self.buttons_general_frame, textvariable=self.rx, width=self.buttons_width, bd='2')
        self.xEntry.bind('<KeyRelease>', self.set_xyz)
        self.xEntry.grid(row=0, column=3, sticky='ns')

        self.yEntry = tk.Entry(self.buttons_general_frame, textvariable=self.ry, width=self.buttons_width, bd='2')
        self.yEntry.bind('<KeyRelease>', self.set_xyz)
        self.yEntry.grid(row=1, column=3, sticky='nsew')

        self.zEntry = tk.Entry(self.buttons_general_frame, textvariable=self.num_of_sample, width=self.buttons_width, bd='2')
        self.zEntry.bind('<KeyRelease>', self.set_xyz)
        self.zEntry.grid(row=2, column=3, sticky='nsew')

        tk.Button(self.buttons_general_frame, text='Calibration', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.robot_calibration).grid(row=3, column=0, sticky='nsew')

        tk.Button(self.buttons_general_frame, text='Pick', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.set_transformation_state).grid(row=3, column=1,
                                                                                            sticky='nsew')

    def set_xyz(self, event):
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]
        self.circle_param = [self.rx.get(), self.ry.get(), self.num_of_sample.get()]
        logging.info('CVController: Target pos was set to %s, %s', str(self.world_coord), str(self.circle_param))
        self.robot_manager.set_draw_param(self.world_coord, self.circle_param)
        # print('Coord: ', self.world_coord)

    def generate_rand_xyz(self):
        self.x.set(np.random.randint(-40, 40, size=1)[0])
        self.y.set(np.random.randint(-40, -10, size=1)[0])
        self.z.set(3)
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]

    def go_to(self):
        logging.info('CVController: Go to %s', str(self.world_coord))
        self.robot_manager.set_current_pos(self.world_coord)

    def set_depth_frame_to_canvas(self):
        frame_depth, frame_rgb = self.robot_manager.get_depth_frame_data()
        if len(frame_rgb)>0:
            self.frame_rgb = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.background_canvas.create_image(0, 0, image=self.frame_rgb, anchor='nw')
            # self.frame_depth = ImageTk.PhotoImage(image=Image.fromarray(frame_depth))
            # self.video_depth_canvas.create_image(0, 0, image=self.frame_depth, anchor='nw')

    def set_frame_to_canvas(self):
        frame, red_only, diff_red, rect = self.robot_manager.get_frame_data()
        frame = self.show_rects(frame, rect)

        self.frame = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.video_canvas.create_image(0, 0, image=self.frame, anchor='nw')
        self.red_only = ImageTk.PhotoImage(image=Image.fromarray(red_only))
        self.signal_canvas.create_image(0, 0, image=self.red_only, anchor='nw')

    def show_rects(self, frame, rect):
        if (len(rect) > 0):
            x = rect[0]
            y = rect[1]
            w = rect[2]
            h = rect[3]
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame

    def save_background(self):
        logging.info('CVController: Saving background')
        self.background = self.robot_manager.save_background(True)
        self.image = ImageTk.PhotoImage(image=Image.fromarray(self.background))
        self.background_canvas.create_image(0, 0, image=self.image, anchor='nw')

    def set_target_obj(self, *args):
        target_obj = self.target_obj.get()
        self.robot_manager.set_target_obj(target_obj)

    def clear_data(self):
        logging.info('CVController: Reset buffers')
        self.robot_manager.reset_buffers()

    def save_data(self):
        logging.info('CVController: Saving data')
        # self.robot_manager.set_store_flg(self.store_flg.get())
        self.robot_manager.save_data()

    def draw_circle(self):
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]
        self.circle_param = [self.rx.get(), self.ry.get(), self.num_of_sample.get()]
        logging.info('CVController: Draw params %s, %s', str(self.world_coord), str(self.circle_param))
        self.robot_manager.set_draw_param(self.world_coord, self.circle_param)
        self.robot_manager.start_draw()
        logging.info('ControlPannel: Drawing circle')

    def set_transformation_state(self):
        self.robot_manager.set_transformation_state()

    def robot_calibration(self):
        self.world_coord = [self.x.get(), self.y.get(), self.z.get()]
        self.circle_param = [self.rx.get(), self.ry.get(), self.num_of_sample.get()]
        logging.info('CVController: Calibration %s, %s', str(self.world_coord), str(self.circle_param))
        self.background = self.robot_manager.set_calibration(self.world_coord, self.circle_param)
        self.image = ImageTk.PhotoImage(image=Image.fromarray(self.background))
        self.background_canvas.create_image(0, 0, image=self.image, anchor='nw')

    def restart(self):
        logging.info('ControlPannel: Restart')

    def stop(self):
        self.run = not(self.run)
        self.robot_manager.set_state(self.run)

        logging.info('ControlPannel: Running %d ', self.run)
        if self.run:
            tk.Button(self.buttons_frame, text='Stop', width=self.buttons_width,
                  height=self.buttons_height, bd='10', command=self.stop).grid(row=0, column=2, sticky='nsew')
        else:
            tk.Button(self.buttons_frame, text='Run', width=self.buttons_width,
                      height=self.buttons_height, bd='10', command=self.stop).grid(row=0, column=2, sticky='nsew')
