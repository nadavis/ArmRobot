import yaml
import tkinter as tk
import time

class ParamsManger:
    def __init__(self, container, arduino_msg, config):
        self.config = config
        # code for creating table
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        self.container = container
        self.arduino_msg = arduino_msg
        lst = config['servo_spec']['min']
        self.num_of_joint = len(lst)

        root = tk.Frame(container)
        root.grid(column=0, row=0)
        self.root = root

        self.createTable(root, config)
        self.createButton()

    def createTable(self, root, config):
        tk.Label(root, text='Min').grid(column=1, row=0)
        tk.Label(root, text='Max').grid(column=2, row=0)
        tk.Label(root, text='Home').grid(column=3, row=0)
        for i in range(0, self.num_of_joint):
            tk.Label(root, text=('Joint',i+1)).grid(column=0, row=i+1)

        self.min_serov_str_list = self.setServoParams(root, 1, config['servo_spec']['min'])
        self.max_serov_str_list = self.setServoParams(root, 2, config['servo_spec']['max'])
        self.home_serov_str_list = self.setServoParams(root, 3, config['servo_spec']['home'])

    def setServoParams(self, root, ind, lst):
        _str_list = []
        for j in range(0, self.num_of_joint):
            _str = tk.StringVar()
            self.e = tk.Entry(root, width=20, textvariable=_str, takefocus=False)
            self.e.grid(row=1+j, column=ind)
            self.e.insert(0, lst[j])
            _str_list.append(_str)
        return _str_list

    def show_values(self):
        for i in range(0, self.num_of_joint):
            print('Joint' + str(i+1) + ': Min, Max, Home |', self.min_serov_str_list[i].get(), self.max_serov_str_list[i].get(), self.home_serov_str_list[i].get())

    def saveYml(self):
        print('saveYml')
        for i in range(0, self.num_of_joint):
            self.config['servo_spec']['home'][i] = self.home_serov_str_list[i].get()
            self.config['servo_spec']['min'][i] = self.min_serov_str_list[i].get()
            self.config['servo_spec']['max'][i] = self.max_serov_str_list[i].get()
        with open('config.yml', 'w') as file:
            documents = yaml.dump(self.config, file)

    def setConfig(self):
        print('set Yml')
        for i in range(0, self.num_of_joint):
            self.config['servo_spec']['home'][i] = self.home_serov_str_list[i].get()
            self.config['servo_spec']['min'][i] = self.min_serov_str_list[i].get()
            self.config['servo_spec']['max'][i] = self.max_serov_str_list[i].get()
        print(self.config)

    def sendParams(self):
        print('setParams')
        for i in range(0, self.num_of_joint):
            self.msgStructure('min', i, self.min_serov_str_list[i].get())
            self.msgStructure('max', i, self.max_serov_str_list[i].get())
            self.msgStructure('home', i, self.home_serov_str_list[i].get())

    def msgStructure(self, name, i, val):
        msg = name + ':' + str(i) + ':' + str(val)
        print(msg)
        self.arduino_msg.sendToArduino(msg)
        time.sleep(0.1)

    def createButton(self):
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)
        self.buttons_frame = tk.Frame(self.container)
        self.buttons_frame.grid(column=0, row=1)
        rndButton = tk.Button(self.buttons_frame, text='Show', width=20, height=5, bd='10', command=lambda: self.show_values())
        rndButton.grid(row=0, column=0, sticky='ns')
        spanButton = tk.Button(self.buttons_frame, text='Save', width=20, height=5, bd='10', command=self.saveYml)
        spanButton.grid(row=1, column=0, sticky='ns')
        homeButton = tk.Button(self.buttons_frame, text='Send', width=20, height=5, bd='10', command=self.sendParams)
        homeButton.grid(row=0, column=1, sticky='ns')
        setButton = tk.Button(self.buttons_frame, text='Set', width=20, height=5, bd='10', command=self.setConfig)
        setButton.grid(row=1, column=1, sticky='ns')
