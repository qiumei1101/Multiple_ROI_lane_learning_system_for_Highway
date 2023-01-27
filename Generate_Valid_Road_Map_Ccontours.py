import math

import cv2
import os
import numpy as np
# from test_dbscan import main as dbscan
import  matplotlib.pyplot as plt
def generate_contour(learning_cycle,binary_image,frame,filepath):
    cnts = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    min_area =12000
    max_area = 6000000
    remain_cnts=[]

    for c in cnts:
        area = cv2.contourArea(c)
        [vx, vy, x0, y0] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)

        angle = math.atan(-vy / vx) * 180 / math.pi
        # print("angle",angle)
        if area > min_area and area < max_area and abs(angle)>5:
            cv2.drawContours(frame, [c], -1, (255, 0, 0), 2)
            remain_cnts.append(c)

    cv2.imwrite(os.path.join(filepath, str(learning_cycle)+'_'+'contour_on_roadmap.png'), frame)
    return remain_cnts