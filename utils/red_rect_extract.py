import os, glob
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ./data/20220718_134705.jpg [(1921, 1768), (2562, 2363)]
# ./data/20220718_134700.jpg [(1631, 994), (3296, 2341)]
# ./data/20220718_134649.jpg [(1496, 1165), (2540, 2126)]
# ./data/20220718_134654.jpg [(1276, 133), (2621, 1764)]
# ./data/20220718_134657.jpg [(1687, 2076), (3355, 2857)]

# df = pd.DataFrame(columns=['path', 'a', 'b'])
# df.to_csv()

def click_event(event, x, y, flags, params):
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt.append((x, y))
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(x) + ',' +
                    str(y), (x, y), font,
                    5, (255, 255, 255), 3)
        if len(refPt) == 2:
            cv2.rectangle(img, refPt[0], refPt[1], (255, 255, 255), 2)
            cv2.imshow('image', img)
            print(image_path, refPt)
            d = pd.DataFrame([[image_path, refPt[0], refPt[1]]], columns=['path', 'a', 'b'])
            d.to_csv(df_path, mode='a', header=False)
            # df = df.append(d)
            print(d)
            # print(df)


if __name__ == "__main__":
    refPt = []
    scale_percent = 25
    df = pd.DataFrame(columns=['path', 'a', 'b'])
    df_path = 'data/rect.csv'
    df.to_csv(df_path)
    path = './data'

    for image_path in glob.glob(os.path.join(path, '*.jpg')):
        img = cv2.imread(image_path)
        cv2.imshow('image', img)
        cv2.setMouseCallback('image', click_event)
        # df = df.append(d)
        cv2.waitKey(0)
        refPt = []
    cv2.destroyAllWindows()