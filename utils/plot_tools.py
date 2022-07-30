import matplotlib.pyplot as plt
import numpy as np

class PlotTools:
    def __init__(self, links_size):
        self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"})
        self.links_size = links_size

    def draw_points(self, vx,vy,vz, c='m', linewidth=2):
        self.ax.scatter(vx, vy, vz, c=c, marker='o', linewidth=linewidth)
        plt.draw()
        plt.pause(0.01)

    def draw_circle(self, vx,vy,vz, c='m', linewidth=2):
        self.ax.plot(vx, vy, vz, c=c, linewidth=linewidth)
        plt.draw()
        plt.pause(0.01)

    def show_kinematics(self, theta, H, T, c='g', linewidth=2, x0=0, y0=0, z0=0):
        # theta = self.kinematics.theta
        # for i in range(0, self.num_of_joint-1):
        #     theta[i] = self.joint_slider[i].get_slider_angel()
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

        plt.cla()
        self.ax.plot(x0, y0, z0, c='m', marker='o')
        self.ax.plot(x, y, z, c='r', marker='o')
        self.ax.plot(x, y, z, c=c, linewidth=linewidth)
        self.ax.plot(x_, y_, z_, c='b', marker='o')
        self.ax.set_xlim(-ma, ma)
        self.ax.set_ylim(-ma, ma)
        self.ax.set_zlim(0, ma)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        # plt.show(block=False)
        # plt.show()
        plt.draw()
        plt.pause(0.01)
