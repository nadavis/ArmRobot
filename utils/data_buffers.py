import numpy as np
import logging
import matplotlib.pyplot as plt

try:
    import utils.transformation_wizard as tw
    import utils.trans_wizard as trans_w
    from utils.plot_tools import PlotTools
except:
    import transformation_wizard as tw
    import trans_wizard as trans_w
    from plot_tools import PlotTools


class DataBuffer():
    def __init__(self, max_size, thetas_shape, pos_shape, pixel_shape, load_data=False):
        self.mem_size = max_size
        self.thetas_shape = thetas_shape
        self.pos_shape = pos_shape
        self.pixel_shape = pixel_shape
        self.outfile = './data/'
        self.reset()
        if(load_data):
            self.load(self.outfile)

    def is_empty(self):
        return self.counter == 0

    def reset(self):
        self.index = 0
        self.counter = 0
        self.thetas_memory = np.zeros((self.mem_size, self.thetas_shape))
        self.pos_memory = np.zeros((self.mem_size, self.pos_shape))
        self.pixel_memory = np.zeros((self.mem_size, self.pixel_shape))
        self.terminal_memory = np.zeros(self.mem_size)

    def set_rand(self):
        # Random rotation and translation
        self.R_pixel_pos = np.random.rand(3, 3)
        self.t_pixel_pos = np.random.rand(3, 1)+2

        # make R a proper rotation matrix, force orthonormal
        U, S, Vt = np.linalg.svd(self.R_pixel_pos)
        self.R_pixel_pos = U @ Vt

        if np.linalg.det(self.R_pixel_pos) < 0:
            Vt[2, :] *= -1
            self.R_pixel_pos = U @ Vt

        self.pixel_memory = np.random.rand(self.mem_size, self.pixel_shape)
        self.pos_memory = self.R_pixel_pos @ self.pixel_memory.T + self.t_pixel_pos
        self.pos_memory[0,:] = self.pos_memory[0,:]
        self.pos_memory[1,:] = 2*self.pos_memory[1,:]+2
        self.pos_memory[2,:] = -5*self.pos_memory[2,:]+7
        self.pos_memory = self.pos_memory.T

    def set(self, thetas, pos, pixel):
        logging.info('DataBuffer: Set data to buffer. thetas %s, pos %s, pixel %s', str(thetas), str(pos), str(pixel))
        # print(self.pixel_memory)
        self.counter += 1
        index = self.index % self.mem_size
        self.thetas_memory[index] = thetas
        self.pos_memory[index] = pos
        self.pixel_memory[index] = pixel
        self.terminal_memory[index] = self.counter
        self.index += 1

    def save(self):
        if sum(sum(self.thetas_memory))>0:
            logging.info('DataBuffer: Saving data to buffer.')
            np.save(self.outfile+'thetas_memory', self.thetas_memory)
            np.save(self.outfile + 'pos_memory', self.pos_memory)
            np.save(self.outfile + 'pixel_memory', self.pixel_memory)
            np.save(self.outfile + 'terminal_memory', self.terminal_memory)
        else:
            logging.error('DataBuffer: Data buffer is empty, buffer not been saved')

    def save_trans_mat(self):
        if sum(sum(self.thetas_memory))>0:
            logging.info('DataBuffer: Saving transformation matrix.')
            np.save(self.outfile + 'H_pixel_pos', self.H_pixel_pos)
            np.save(self.outfile + 'H_pos_pixel', self.H_pos_pixel)
        else:
            logging.error('DataBuffer: Data buffer is empty, transformation not been saved')

    def load(self, path=[]):
        if len(path)>0:
            self.outfile = path
        logging.info('DataBuffer: Loading data to buffer.')
        self.thetas_memory = np.load(self.outfile+'thetas_memory.npy')
        self.pos_memory = np.load(self.outfile + 'pos_memory.npy')
        self.pixel_memory = np.load(self.outfile + 'pixel_memory.npy')
        self.terminal_memory = np.load(self.outfile + 'terminal_memory.npy')
        try:
            self.H_pixel_pos = np.load(self.outfile + 'H_pixel_pos.npy')
            self.H_pos_pixel = np.load(self.outfile + 'H_pos_pixel.npy')
        except:
            logging.error('DataBuffer: No transformation matrix is exists.')

    def get(self, ind):
        thetas = self.thetas_memory[ind]
        pos = self.pos_memory[ind]
        pixel = self.pixel_memory[ind]
        return thetas, pos, pixel

    def transpose_array(self):
        self.pos_memory = np.transpose(self.pos_memory)
        self.pixel_memory = np.transpose(self.pixel_memory)
        self.thetas_memory = np.transpose(self.thetas_memory)

    # def remove_zeros(self):
    #     ind = self.terminal_memory != 0
        # self.pos_memory = self.pos_memory[ind]
        # self.pixel_memory = self.pixel_memory[ind]
        # self.thetas_memory = self.thetas_memory[ind]

    def trans_matrix(self):
        logging.info('DataBuffer: calc transformation matrix.')
        ind = self.terminal_memory != 0
        logging.info('DataBuffer: Pixel array %s', str(self.pixel_memory[ind]))
        logging.info('DataBuffer: Pos array %s', str(self.pos_memory[ind]))
        self.H_pixel_pos = tw.least_squares_transform(self.pixel_memory[ind], self.pos_memory[ind])
        self.H_pos_pixel = tw.least_squares_transform(self.pos_memory[ind], self.pixel_memory[ind])

    def apply_trans_pixel_pos(self, pixel):
        # if(len(pixel)>0):
        #     self.pixel_memory = pixel
        logging.info('DataBuffer: Apply pixel to pos transformation matrix %s on pixel %s ', str(self.H_pixel_pos), str(pixel))
        B = tw.apply_ls_trans(self.H_pixel_pos, pixel)
        logging.info('DataBuffer: Result transformation matrix  %s ', str(B.T))
        return B.T

    def apply_trans_pos_pixel(self, pos):
        # if (len(pos) > 0):
        #     self.pos_memory = pos
        logging.info('DataBuffer: Apply pos to pixel transformation matrix on pos %s ', str(pos))
        B = tw.apply_ls_trans(self.H_pos_pixel, pos)
        logging.info('DataBuffer: Result transformation matrix  %s ', str(B.T))
        return B.T

if __name__ == "__main__":

    db = DataBuffer(100, 5, 3, 3)

    db.set_rand()
    db.load('../data/')

    # db.remove_zeros()
    db.trans_matrix()

    ind = db.terminal_memory != 0
    pos = db.apply_trans_pixel_pos(db.pixel_memory[ind])
    pixel = db.apply_trans_pos_pixel(db.pos_memory[ind])
    # db.save_trans_mat()

    print(db.apply_trans_pixel_pos(np.array([[200,100,0]])))

    # Find the root mean squared error
    err = pos - db.pos_memory[ind].T
    err = err * err
    err = np.sum(err)
    rmse = np.sqrt(err/db.mem_size)
    print("RMSE:", rmse)

    err = pixel - db.pixel_memory[ind].T
    err = err * err
    err = np.sum(err)
    rmse = np.sqrt(err / db.mem_size)
    print("RMSE:", rmse)


    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x = pos[0,:]
    y = pos[1,:]
    z = pos[2,:]
    ax.scatter(x, y, z, c='b', marker='o')
    x = pixel[0, :]
    y = pixel[1, :]
    z = pixel[2, :]
    ax.scatter(x, y, z, c='r', marker='o')
    pos_memory = db.pos_memory[ind].T
    x = pos_memory[0, :]
    y = pos_memory[1, :]
    z = pos_memory[2, :]
    ax.scatter(x, y, z, c='r', marker='x')
    pixel_memory = db.pixel_memory[ind].T
    x = pixel_memory[0, :]
    y = pixel_memory[1, :]
    z = pixel_memory[2, :]
    ax.scatter(x, y, z, c='b', marker='x')

    plt.show()