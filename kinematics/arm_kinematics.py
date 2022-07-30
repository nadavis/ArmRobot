import yaml
import numpy as np
import matplotlib.pyplot as plt
import math
import time

class ArmKinematics():
    def __init__(self, kinematics_config, servo_config):
        a = kinematics_config['link_size']
        theta0 = kinematics_config['theta0']
        self.theta = [0, 0, 0, 0, 0]
        self.pwm = servo_config['home']
        self.prev_theta = self.theta
        self.theta0 = theta0
        self.a = a
        self.theta_limit = 90
        self.num_of_theta = 3
        self.num_of_dof = 5
        self.avoid_collision = kinematics_config['enable_collision']
        self.gripper_state = kinematics_config['gripper_state']
        self.z_limit = kinematics_config['z_limit']

        # self.max_angel_motor_spec = np.array(servo_config['angel_max'])
        # self.max_motor_spec = np.array(servo_config['pwm_max'])
        # self.gear_spec = np.array(servo_config['gear_ratio'])
        # self.min_motor_spec = np.array(servo_config['pwm_min'])
        # self.pwm2angel = self.max_angel_motor_spec / (self.gear_spec*(self.max_motor_spec-self.min_motor_spec))
        # self.home_motor = np.array(servo_config['home'])
        # self.min_motor = np.array(servo_config['min'])
        # self.max_motor = np.array(servo_config['max'])
        # self.servo_direction = np.array(servo_config['servo_direction'])

        self.d_h_table = np.array([[np.deg2rad(theta0[0]), np.deg2rad(90), 0, a[0]],
                                   [np.deg2rad(theta0[1]+90), np.deg2rad(0), a[1], 0],
                                   [np.deg2rad(theta0[2] + 90), np.deg2rad(90), a[3], 0],
                                   [np.deg2rad(theta0[3]), np.deg2rad(-90), a[4], a[2] + a[5]],
                                   [np.deg2rad(theta0[4] - 90), np.deg2rad(0), 0, 0],
                                   [np.deg2rad(0), np.deg2rad(0), a[6], 0]])


    def rot_tran_matrix(self, theta, alpha, r, d):
        return np.array([[np.cos(theta), -np.sin(theta) * np.cos(alpha),
                                np.sin(theta) * np.sin(alpha),
                                r * np.cos(theta)],
                               [np.sin(theta), np.cos(theta) * np.cos(alpha),
                                -np.cos(theta) * np.sin(alpha),
                                r * np.sin(theta)],
                               [0, np.sin(alpha), np.cos(alpha), d],
                               [0, 0, 0, 1]])

    # def pwm_2_angel(self, ind, val):
    #     print([val, ind])
    #     return (val-self.home_motor[ind])*self.pwm2angel[ind]
    #
    # def angel_2_pwm_by(self, ind, val):
    #     val = val * self.servo_direction[ind]
    #     return self.home_motor[ind]+val/self.pwm2angel[ind]
    #
    # def angel_2_pwm(self):
    #     val = self.theta * self.servo_direction[:len(self.theta)]
    #     self.pwm = self.home_motor[:len(self.theta)]+val/self.pwm2angel[:len(self.theta)]
    #     # print(self.pwm)

    def set_avoid_collision(self, flg):
        self.avoid_collision = flg

    def set_gripper_state(self, flg):
        self.gripper_state = flg
        if self.gripper_state=='None':
            self.theta[3] = 0
            self.theta[4] = 0

    def inv_kinematics(self, pos, offest_z=0, offeset_d=0, offset_a=0):
        a0 = self.a[0]
        a1 = self.a[1]
        a2 = self.a[2] + self.a[5] + offset_a

        t0 = np.arctan2(pos[1], pos[0])
        if (pos[0] <= 0 and pos[1] >= 0):
            t0 = t0-math.pi
        elif (pos[0] < 0 and pos[1] < 0):
            t0 = math.pi+t0

        pos[0] = pos[0] + offeset_d * np.cos(t0)
        pos[1] = pos[1] + offeset_d * np.sin(t0)
        y = np.sqrt(pos[0] * pos[0] + pos[1] * pos[1])
        # y = y - offeset_d
        # if(y>offeset_d):
        #     y = y - offeset_d
        # else:
        #     y = y + offeset_d
        x = pos[2] - a0 + offest_z

        sign_x = x
        # sign_y = y
        x = np.abs(x)
        k0 = (x * x + y * y - a1 * a1 - a2 * a2) / (2 * a1 * a2)

        if(k0>1):
            if (k0 < 1.00001):
                k0 = 1
            else:
                print('NO RESULTS')
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
        if(len(theta)==0):
            theta = self.theta
        if num_of_frames==0:
            num_of_frames = len(self.d_h_table)

        for i in range(len(theta), num_of_frames):
            theta = np.append(theta, 0)

        for i in range(0, num_of_frames):
            res = self.rot_tran_matrix(self.d_h_table[i, 0]+np.deg2rad(theta[i]), self.d_h_table[i, 1], self.d_h_table[i, 2], self.d_h_table[i, 3])
            T = T @ res
            H.append(res)
            if(i>0):
                is_collision = is_collision or self.check_collision(T)
                if is_collision and self.avoid_collision:
                    print('colission: ', T[:3, 3], ' flg: ', T[2,3]<= self.z_limit)

        return np.round(H, 5), np.round(T, 5), is_collision

    def pos_gripper_horizontal(self, theta=[]):
        if (len(theta) > 0):
            self.theta = theta

        if (len(self.theta) == len(self.theta0)):
            self.theta[3] = 0
            self.theta[4] = (90 - self.theta[1] - self.theta[2])
        else:
            self.theta = np.append(self.theta, 0)
            self.theta = np.append(self.theta, 90 - self.theta[1] - self.theta[2])

        return self.theta

    def pos_gripper_down(self, theta=[]):
        if(len(theta)>0):
            self.theta = theta
        if(len(self.theta) == len(self.theta0)):
            self.theta[3] = 0
            self.theta[4] = 180 - self.theta[1] - self.theta[2]
        else:
            self.theta = np.append(self.theta, 0)
            self.theta = np.append(self.theta, 180 - self.theta[1] - self.theta[2])

        return self.theta

    def pos_gripper_none(self, theta=[]):
        if(len(theta)>0):
            self.theta = theta
        if(len(self.theta) == len(self.theta0)):
            self.theta[3] = 0
            self.theta[4] = 0
        else:
            self.theta = np.append(self.theta, 0)
            self.theta = np.append(self.theta, 0)

        return self.theta

    def set_theta_by_motor_ind(self, motor_ind, theta):
        if(motor_ind<len(self.theta)):
            self.theta[motor_ind] = theta
        return self.theta

    def run_forward_kinematics(self, theta=[]):
        # print("--- KINEMATIC START---")
        # print('theta:', self.theta)
        # print('prev theta:', self.prev_theta)

        if(len(theta)>0):
            for i in range(len(theta), len(self.theta)):
                theta = np.append(theta, 0)
            self.theta = theta

        if(self.gripper_state == 'Vertical'):
            self.theta = self.pos_gripper_down(self.theta)
        elif(self.gripper_state == 'Horizontal'):
            self.theta = self.pos_gripper_horizontal(self.theta)
        elif(self.gripper_state == 'None'):
            self.theta[3] = 0
            self.theta[4] = 0


        H, T, is_collision = self.run_forward(self.theta)
        is_collision = is_collision and self.avoid_collision
        if is_collision:
            print("--- KINEMATIC COLLISION---")
            print('theta:', self.theta)
            print('prev theta:', self.prev_theta)
            H, T, is_collision = self.run_forward(self.prev_theta)
            self.theta = self.prev_theta.copy()
        else:
            self.prev_theta = self.theta.copy()
        # print('update theta:', self.theta)
        pos = T[:3, 3]
        self.angel_2_pwm()
        return self.theta, pos, is_collision, np.round(H, 5), np.round(T, 5)

    def check_collision(self, T):
        if(T[2,3]<= self.z_limit):
            return True
        return False

    def go_home(self):
        theta = self.theta0
        H, T, is_collision = self.run_forward(theta)

    # def check_collision_by_theta(self, theta=[]):
    #     if(len(theta)==0):
    #         theta = self.theta
    #     H, T, is_collision = self.run_forward(theta)
    #     return is_collision

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

    with open("config.yml", 'r') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
    show = True
    k = ArmKinematics(config)
    k.avoid_collision = False
    k.gripper_state = False
    err1 = []
    err2 = []
    err_min=[]
    errp1 = []
    errp2 = []
    errp_min = []
    b_vertical = 2
    for t in range(0, 1000, 1):
        theta0 = np.random.randint(-90, 90, size=len(k.theta0))
        # theta0[0]=0
        H0, T0, is_collision = k.run_forward(theta0)
        pos0_ = T0[:3, 3]
        if(b_vertical==0):
            theta0 = k.pos_gripper_down(theta0)
        elif(b_vertical==1):
            theta0 = k.pos_gripper_horizontal(theta0)
        elif (b_vertical == 2):
            theta0 = k.pos_gripper_none(theta0)

        H0, T0, is_collision = k.run_forward(theta0)
        pos0 = T0[:3, 3]
        offset_a = 0
        if (b_vertical==0):
            offset_z = k.a[6]
            offset_d = 0
        elif (b_vertical==1):
            offset_d = k.a[6]
            offset_z = 0
        elif (b_vertical==2):
            offset_a = k.a[6]
            offset_z = 0
            offset_d = 0

        theta1, theta2 = k.inv_kinematics(pos0.copy(), offset_z, offset_d, offset_a)
        # if(len(theta1)==0 or len(theta2)==0):
        #     print('No results')
        #     continue
        if (b_vertical==0):
            theta1 = k.pos_gripper_down(theta1)
            theta2 = k.pos_gripper_down(theta2)
        elif (b_vertical == 1):
            theta1 = k.pos_gripper_horizontal(theta1)
            theta2 = k.pos_gripper_horizontal(theta2)
        elif (b_vertical == 2):
            theta1 = k.pos_gripper_none(theta1)
            theta2 = k.pos_gripper_none(theta2)

        H1, T1, is_collision = k.run_forward(theta1)
        pos1 = T1[:3, 3]
        H2, T2, is_collision = k.run_forward(theta2)
        pos2 = T2[:3, 3]

        # pos0[2] = pos0[2] - k.a[6]

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

