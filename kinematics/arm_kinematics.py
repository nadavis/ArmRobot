from ops.config_ops import ConfigOps
import numpy as np
import matplotlib.pyplot as plt
import math
import logging

class ArmKinematics():
    def __init__(self, config):
        a = config.get_links_size()
        theta0 = config.get_thetas_zero()
        # self.avoid_collision = config.get_enable_collision_state()
        self.gripper_state = config.get_gripper_state()
        self.z_limit = config.get_z_limit()

        self.a = a
        self.num_of_dof = 5
        self.d_h_table = np.array([[np.deg2rad(theta0[0]), np.deg2rad(90), 0, a[0]],
                                   [np.deg2rad(theta0[1]+90), np.deg2rad(0), a[1], 0],
                                   [np.deg2rad(theta0[2] + 90), np.deg2rad(90), a[3], 0],
                                   [np.deg2rad(theta0[3]), np.deg2rad(-90), a[4], a[2] + a[5]],
                                   [np.deg2rad(theta0[4] - 90), np.deg2rad(0), 0, 0],
                                   [np.deg2rad(0), np.deg2rad(0), a[6], 0]])

    def get_number_of_dof(self):
        return self.num_of_dof

    def rot_tran_matrix(self, theta, alpha, r, d):
        return np.array([[np.cos(theta), -np.sin(theta) * np.cos(alpha),
                                np.sin(theta) * np.sin(alpha),
                                r * np.cos(theta)],
                               [np.sin(theta), np.cos(theta) * np.cos(alpha),
                                -np.cos(theta) * np.sin(alpha),
                                r * np.sin(theta)],
                               [0, np.sin(alpha), np.cos(alpha), d],
                               [0, 0, 0, 1]])

    # def run_inv_kinematics(self, pos):
    #     offset_z, offset_d, offset_a = self.get_gripper_parameters()

    def inv_kinematics(self, pos, offset_z=0, offset_d=0, offset_a=0):
        if (offset_z==0 and offset_d==0 and offset_a==0):
            logging.warning('ArmKinematics: Gripper possition did not set, No movement done')
            return [], []

        a0 = self.a[0]
        a1 = self.a[1]
        a2 = self.a[2] + self.a[5] + offset_a

        t0 = np.arctan2(pos[1], pos[0])
        if (pos[0] <= 0 and pos[1] >= 0):
            t0 = t0-math.pi
        elif (pos[0] < 0 and pos[1] < 0):
            t0 = math.pi+t0

        pos[0] = pos[0] + offset_d * np.cos(t0)
        pos[1] = pos[1] + offset_d * np.sin(t0)
        y = np.sqrt(pos[0] * pos[0] + pos[1] * pos[1])
        # y = y - offeset_d
        # if(y>offeset_d):
        #     y = y - offeset_d
        # else:
        #     y = y + offeset_d
        x = pos[2] - a0 + offset_z

        sign_x = x
        # sign_y = y
        x = np.abs(x)
        k0 = (x * x + y * y - a1 * a1 - a2 * a2) / (2 * a1 * a2)

        if(k0>1):
            if (k0 < 1.00001):
                k0 = 1
            else:
                logging.warning('ArmKinematics: Kinematics is out of range')
                # print('NO RESULTS')
                return [], []

        t2 = np.arccos(k0)
        k1 = a2 * np.sin(t2)
        k2 = a1 + a2 * np.cos(t2)
        t1 = np.arctan2(y, x) - np.arctan2(k1, k2)

        t2_ = np.arccos(k0)
        k1_ = a2 * np.sin(t2_)
        k2_ = a1 + a2 * np.cos(t2_)
        t1_ = np.arctan2(y, x) + np.arctan2(k1_, k2_)

        b_pos = 0
        if (pos[0] > 0 and pos[1] > 0):
            t1 = -t1
            t2 = -t2
            t1_ = -t1_
            t2_ = -t2_
            b_pos = 1
        elif (pos[0] >= 0 and pos[1] <= 0):
            t1 = -t1
            t2 = -t2
            t1_ = -t1_
            t2_ = -t2_
            b_pos = 1

        theta1 = np.round([np.rad2deg(t0), np.rad2deg(t1), np.rad2deg(t2)])
        theta2 = np.round([np.rad2deg(t0), np.rad2deg(t1_), -np.rad2deg(t2_)])

        if(b_pos==0):
            if(sign_x<0):
                theta1 = np.round([np.rad2deg(t0), 180-np.rad2deg(t1), -np.rad2deg(t2)])
                theta2 = np.round([np.rad2deg(t0), 180-np.rad2deg(t1_), np.rad2deg(t2_)])
        elif(b_pos==1):
            if (sign_x < 0):
                theta1 = np.round([np.rad2deg(t0), -(180 + np.rad2deg(t1)), -np.rad2deg(t2)])
                theta2 = np.round([np.rad2deg(t0), -(180 + np.rad2deg(t1_)), np.rad2deg(t2_)])

        if(abs(theta1[0])==360):
            theta1[0] = 0
        if (abs(theta2[0]) == 360):
            theta2[0] = 0
                # theta1 = np.append(theta1, 0)

        if(abs(theta1[1])+abs(theta1[2]) > abs(theta2[1])+abs(theta2[2])):
            tmp = theta2
            theta2 = theta1
            theta1 = tmp
            # print('swap theta')
        # theta1 = np.append(theta1, 0)
        # theta2 = np.append(theta2, 0)
        # theta2 = np.append(theta2, 0)
        return theta1, theta2

    def run_forward(self, theta=[], num_of_frames=0):
        H = []
        T = np.eye(4)
        is_collision = False

        if num_of_frames==0:
            num_of_frames = len(self.d_h_table)

        for i in range(len(theta), num_of_frames):
            theta = np.append(theta, 0)

        logging.info('ArmKinematics: Calc forward kinematics of thetas %s ', str(theta))
        for i in range(0, num_of_frames):
            res = self.rot_tran_matrix(self.d_h_table[i, 0]+np.deg2rad(theta[i]), self.d_h_table[i, 1], self.d_h_table[i, 2], self.d_h_table[i, 3])
            T = T @ res
            H.append(res)
            if(i>0):
                is_collision = is_collision or self.check_collision(T)
                if is_collision:
                    logging.warning('ArmKinematics: Collision at theta ind %d, z value is %d [cm], z limit was set to %d [cm]', i, T[2,3], self.z_limit)
                    # print('Collision: ', T[:3, 3], ' flg: ', T[2,3]<= self.z_limit)

        return np.round(H, 5), np.round(T, 5), is_collision

    def pos_gripper(self, angle, thetas):
        thetas[3] = 0
        thetas[4] = angle - thetas[1] - thetas[2]
        return thetas

    def get_gripper_parameters(self, state):
        offset_a = 0
        offset_z = 0
        offset_d = 0
        if(state == 'Vertical'):
            offset_z = self.a[6]
        elif(state == 'Horizontal'):
            offset_d = self.a[6]
        elif(state=='Home'):
            offset_a = self.a[6]

        logging.info('ArmKinematics: Setting offset_z, offset_d, offset_a: %s ', str([offset_z, offset_d, offset_a]))
        return offset_z, offset_d, offset_a

    def get_gripper_pos(self, state, thetas):
        logging.info('ArmKinematics: Getting gripper pos %s ', state)
        if(state == 'Vertical'):
            thetas = self.pos_gripper(180, thetas)
        elif(state == 'Horizontal'):
            thetas = self.pos_gripper(90, thetas)
        elif(state=='Home'):
            thetas[3] = 0
            thetas[4] = 0

        return thetas

    def run_forward_kinematics(self, state, thetas=[]):
        if(len(thetas)<self.num_of_dof):
            logging.error('ArmKinematics: Number of Thetas less than %d ', self.num_of_dof)

        thetas = self.get_gripper_pos(state, thetas)
        H, T, is_collision = self.run_forward(thetas)

        return thetas, is_collision, np.round(H, 5), np.round(T, 5)

    def check_collision(self, T):
        if(T[2,3]<= self.z_limit):
            return True
        return False

    def show_kinematics(self, H, T, fig=0, ax=0, c='g', linewidth=2, x0=0, y0=0, z0=0):
        ma = sum(self.a)
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
        if fig ==0:
            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax.plot(x0, y0, z0, c='m', marker='o')
        ax.plot(x, y, z, c='r', marker='o')
        ax.plot(x, y, z, c=c, linewidth=linewidth)
        ax.plot(x_, y_, z_, c='b', marker='o')
        ax.set_xlim(-ma, ma)
        ax.set_ylim(-ma, ma)
        ax.set_zlim(0, ma)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # plt.draw()
        # plt.pause(1)
        # plt.show()
        return fig, ax

if __name__ == "__main__":
    pp = []
    for p in range(0,360, 1):
        pp.append(np.rad2deg(np.arctan(p)))

    config = ConfigOps("../config/config.yml")

    show = True
    k = ArmKinematics(config)

    err1 = []
    err2 = []
    err_min=[]
    errp1 = []
    errp2 = []
    errp_min = []
    state = 'Horizontal'
    state = 'Vertical'
    # state = 'Home'

    offset_a = 0
    if (state == 'Vertical'):
        offset_z = k.a[6]
        offset_d = 0
    elif (state == 'Horizontal'):
        offset_d = k.a[6]
        offset_z = 0
    elif(state == 'Home'):
        offset_a = k.a[6]
        offset_z = 0
        offset_d = 0

    for t in range(0, 1000, 1):
        thetas = np.random.randint(-90, 90, size=k.num_of_dof)
        # thetas= [67,  34,  76, - 83,  24]
        thetas, is_collision, H, T = k.run_forward_kinematics(state, thetas)
        pos = T[:3, 3]

        H0 = H
        T0 = T
        theta0 = thetas
        pos0 = pos
        pos0_ = pos


        theta1, theta2 = k.inv_kinematics(pos.copy(), offset_z, offset_d, offset_a)
        theta1 = np.append(theta1,0)
        theta1 = np.append(theta1, 0)
        theta2 = np.append(theta2, 0)
        theta2 = np.append(theta2, 0)
        theta1, is_collision1, H1, T1 = k.run_forward_kinematics(state, theta1)
        pos1 = T1[:3, 3]

        theta2, is_collision2, H2, T2 = k.run_forward_kinematics(state, theta2)
        pos2 = T2[:3, 3]

        d1 = np.subtract(theta0, theta1)
        e1 = np.sqrt(np.mean(d1 * d1))
        err1.append(e1)

        d2 = np.subtract(theta0, theta2)
        e2 = np.sqrt(np.mean(d2 * d2))
        err2.append(e2)

        e = np.min([e1, e2])
        err_min.append(e)

        dp1 = np.subtract(pos0, pos1)
        ep1 = np.sqrt(np.mean(dp1 * dp1))
        errp1.append(ep1)

        dp2 = np.subtract(pos0, pos2)
        ep2 = np.sqrt(np.mean(dp2 * dp2))
        errp2.append(ep2)
        ep = np.min([ep1,ep2])
        errp_min.append(ep)
        # fig, ax = k.show_kinematics(H0, T0, linewidth=4)
        # plt.draw()
        # plt.pause(1)
        if(e>2 or ep>0 or False):
            print('pos', pos0_, pos0, pos1, pos2)
            print('theta', theta0, theta1, theta2)
            print('err theta', e, e1, e2)
            print('err pos', ep, ep1, ep2)
            print('-------------------------------------')
            # H0, T0, is_collision = k.run_forward(theta0)
            fig, ax = k.show_kinematics(H0, T0, linewidth=4)
            fig, ax = k.show_kinematics(H1, T1, fig, ax, 'y', linewidth=2)
            # fig, ax = k.show_kinematics(H2, T2, fig, ax, 'y', linewidth=2)
            # plt.draw()
            # plt.pause(0.1)
            plt.show()
        # time.sleep(10)
    print('theta', np.max(err1), np.max(err2), np.max(err_min))
    print('pos', np.max(errp1), np.max(errp2), np.max(errp_min))

