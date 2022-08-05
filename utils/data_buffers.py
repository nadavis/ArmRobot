import numpy as np
import logging
import transformation_wizard as tw

class DataBuffer():
    def __init__(self, max_size, thetas_shape, pos_shape, pixel_shape):
        self.mem_size = max_size
        self.thetas_shape = thetas_shape
        self.pos_shape = pos_shape
        self.pixel_shape = pixel_shape
        self.outfile = './data/'
        self.reset()

    def reset(self):
        self.index = -1
        self.counter = 0
        self.thetas_memory = np.zeros((self.mem_size, self.thetas_shape))
        self.pos_memory = np.zeros((self.mem_size, self.pos_shape))
        self.pixel_memory = np.zeros((self.mem_size, self.pixel_shape))
        self.terminal_memory = np.zeros((self.mem_size, 1))

    def set_rand(self):
        self.index = -1
        self.counter = 0
        self.thetas_memory = np.random.rand(self.thetas_shape, self.mem_size)
        self.pos_memory = np.random.rand(self.pos_shape, self.mem_size)
        self.pixel_memory = np.random.rand(self.pixel_shape, self.mem_size)
        self.terminal_memory = np.random.rand(1, self.mem_size)

    def set(self, thetas, pos, pixel):
        logging.info('DataBuffer: Set data to buffer. thetas %s, pos %s, pixel %s', str(thetas), str(pos), str(pixel))
        self.index += 1
        index = self.index % self.mem_size
        self.thetas_memory[index] = thetas
        self.pos_memory[index] = pos
        self.pixel_memory[index] = pixel
        self.terminal_memory[index] = self.counter
        self.counter +=1

    def save(self):
        logging.info('DataBuffer: Saving data to buffer.')
        np.save(self.outfile+'thetas_memory', self.thetas_memory)
        np.save(self.outfile + 'pos_memory', self.pos_memory)
        np.save(self.outfile + 'pixel_memory', self.pixel_memory)
        np.save(self.outfile + 'terminal_memory', self.terminal_memory)

    def load(self):
        logging.info('DataBuffer: Loading data to buffer.')
        self.thetas_memory = np.load(self.outfile+'thetas_memory')
        self.pos_memory = np.load(self.outfile + 'pos_memory')
        self.pixel_memory = np.load(self.outfile + 'pixel_memory')
        self.terminal_memory = np.load(self.outfile + 'terminal_memory')

    def get(self, ind):
        thetas = self.thetas_memory[ind]
        pos = self.pos_memory[ind]
        pixel = self.pixel_memory[ind]
        return thetas, pos, pixel

    def trans_matrix(self):
        self.R_pixel_pos, self.t_pixel_pos = tw.rigid_transform_3D(self.pixel_memory, self.pos_memory)
        self.R_pos_pixel, self.t_pos_pixel = tw.rigid_transform_3D(self.pos_memory, self.pixel_memory)

    def apply_trans_pixel_pos(self, pixel):
        return tw.apply_trans(self.R_pixel_pos, self.t_pixel_pos, pixel)

    def apply_trans_pos_pixel(self, pos):
        return tw.apply_trans(self.R_pos_pixel, self.t_pos_pixel, pos)

if __name__ == "__main__":
    db = DataBuffer(10, 5, 3, 3)
    # for i in range(15):
    #     db.set([i,2], [i,2,3], [i,2,3])
    #
    # print(db.terminal_memory)
    db.set_rand()

    # Recover R and t
    db.trans_matrix()
    R = db.R_pos_pixel
    t = db.t_pos_pixel
    # Compare the recovered R and t with the original
    pos = (R@db.pixel_memory) + t

    # Find the root mean squared error
    err = pos - db.pos_memory
    err = err * err
    err = np.sum(err)
    rmse = np.sqrt(err/db.mem_size)

    print("Pixel")
    print(db.pixel_memory)
    print("")

    print("Pos")
    print(db.pos_memory)
    print("")

    print("Ground truth rotation")
    print(R)

    print("Ground truth translation")
    print(t)

    print("RMSE:", rmse)

    if rmse < 1e-5:
        print("Everything looks good!")
    else:
        print("Hmm something doesn't look right ...")
