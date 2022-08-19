import logging
import numpy as np

pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
unpad = lambda x: x[:,:-1]

def least_squares_transform(primary, secondary):

    n = primary.shape[0]

    if n<3:
        logging.error('Transformation wizar: There number of samples should be more than 3, the current number is %d',n)

    pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
    unpad = lambda x: x[:,:-1]
    X = pad(primary)
    Y = pad(secondary)

    A, res, rank, s = np.linalg.lstsq(X, Y, rcond=None)

    return A

def apply_ls_trans(A, primary):
    transform = lambda x: unpad(np.dot(pad(x), A))
    return transform(primary)

if __name__ == "__main__":

    R = np.random.rand(3,3)
    t = np.random.rand(3,1)

    U, S, Vt = np.linalg.svd(R)
    R = U@Vt

    # remove reflection
    if np.linalg.det(R) < 0:
       Vt[2,:] *= -1
       R = U@Vt

    # number of points
    n = 10

    A = np.random.rand(3, n)
    B = R@A + t


    H = least_squares_transform(A, B)
    B_ = apply_ls_trans(H, A)

    err = B_ - B
    err = err * err
    err = np.sum(err)
    rmse = np.sqrt(err/n)

    print("RMSE:", rmse)
