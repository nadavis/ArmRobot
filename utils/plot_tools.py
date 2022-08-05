import matplotlib.pyplot as plt
import numpy as np
import logging
# from matplotlib.figure import Figure


class PlotTools:
    def __init__(self, links_size):
        # plt.ion()
        self.fig = plt.figure(figsize=(2, 2), dpi=100)
        self.ax = self.fig.add_subplot(projection='3d')
        # self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(1, 1))
        self.links_size = links_size
        self.fontsize = 5

    def get_figure(self):
        # x = [1,2,3]
        # y = [1,2,3]
        # z = [1,2,3]
        # self.ax.plot(x, y, z, c='r', linewidth=2)

        return self.fig

    def draw_points(self, vx,vy,vz, c='m', linewidth=2):
        self.ax.scatter(vx, vy, vz, c=c, marker='o', linewidth=linewidth)
        plt.draw()
        plt.pause(0.01)

    def draw_circle(self, vx,vy,vz, c='m', linewidth=2):
        self.ax.plot(vx, vy, vz, c=c, linewidth=linewidth)
        # plt.draw()
        # plt.pause(0.01)

    def clean_plot(self):
        plt.cla()

    def show_kinematics(self, H, T, c='g', linewidth=2, x0=0, y0=0, z0=0):
        logging.info('PlotTools: Show thetas T = %s', str(T))
        ma = sum(self.links_size)
        x = []
        y = []
        z = []
        coords = []
        v = [0, 0, 0, 1]
        x.append(v[0])
        y.append(v[1])
        z.append(v[2])
        T_ = np.eye(4)
        for h in H:
            T_ = T_ @ h
            res = T_ @ v
            x.append(res[0])
            y.append(res[1])
            z.append(res[2])
            coords.append(res)

        res = T @ v
        x_ = res[0]
        y_ = res[1]
        z_ = res[2]

        # plt.cla()
        self.ax.plot(x0, y0, z0, c='m', marker='o')
        self.ax.plot(x, y, z, c='r', marker='o')
        self.ax.plot(x, y, z, c=c, linewidth=linewidth)
        self.ax.plot(x_, y_, z_, c='b', marker='o')
        self.ax.set_xlim(-ma, ma)
        self.ax.set_ylim(-ma, ma)
        self.ax.set_zlim(0, ma)
        self.ax.set_xlabel("X", fontsize=self.fontsize)
        self.ax.set_ylabel("Y", fontsize=self.fontsize)
        self.ax.set_zlabel("Z", fontsize=self.fontsize)
        plt.xticks(fontsize=self.fontsize)
        plt.yticks(fontsize=self.fontsize)
        self.ax.tick_params('z', labelsize=self.fontsize)

        # plt.show(block=False)
        # plt.show()
        # plt.draw()
        # plt.pause(0.01)

        return self.fig
