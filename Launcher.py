import tkinter as tk
from tkinter import ttk
from ui.control_panel import ControlPannel
from ops.robot_manager import RobotManager
from ui.cv_controller import CVController
import logging

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.app_name = 'Arm controller'
        logging.basicConfig(filename='logs/'+self.app_name+'.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        logging.info('Started' + self.app_name)

        self.protocol("WM_DELETE_WINDOW", self.close)


        self.win_width = 1000
        self.win_height = 1000
        self.resizable(True, True)
        self.title(self.app_name)

        notebook = ttk.Notebook(self)
        self.frame_cp = tk.Frame(notebook, height=self.win_height, width=self.win_width)
        self.frame_setup = tk.Frame(notebook, height=self.win_height, width=self.win_width)
        self.frame_cv = tk.Frame(notebook, height=self.win_height, width=self.win_width)
        notebook.add(self.frame_cp, text='Control panel')
        notebook.add(self.frame_setup, text='Setup')
        notebook.add(self.frame_cv, text='CV controllers')
        notebook.columnconfigure(0, weight=1)
        notebook.rowconfigure(0, weight=1)
        notebook.pack(expand=1, fill="both")

        robot_manager = RobotManager()
        self.control_panel = ControlPannel(self.frame_cp, robot_manager, enable_collision=True)
        self.cv_controller = CVController(self.frame_cv, robot_manager)

        self.updater()
        self.mainloop()

    def updater(self):
        self.cv_controller.get_frame()
        self.update()
        self.after(15, self.updater)

    def close(self):
        logging.info('Finished')
        self.destroy()

if __name__ == "__main__":
    app = App()
