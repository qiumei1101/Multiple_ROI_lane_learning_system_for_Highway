import time
from vehicle_detection import Vehicle_Detection_in_continuous_learning
import cv2
from confidence_score import confidence_score
from create_heatmap import create_heatmap
import pickle
import os
import os.path
from blob_detection import blob_detection
import numpy as np
os.system("clear")
times_start = time.time()
count = 0
vehicle_collected=False

while(time.time() - times_start < 240):

    if not os.path.exists('./heatmap_data/collect_vehicles_3.dat'):
        collect_vehicles, collect_cars, frame, camera_angle_changed_ELS = Vehicle_Detection_in_continuous_learning(
            vehicle_collected, count)

        if time.time() - times_start >= 240:
            vehicle_collected = True

        if vehicle_collected:

            h,w = frame.shape[:2]
            pickle.dump(collect_vehicles,open("./heatmap_data/collect_vehicles_3.dat","wb"))
            create_heatmap(collect_vehicles, frame)

            current_time = time.time()
            cv2.imwrite("frame.jpg",frame)
            for veh in collect_vehicles:
                cv2.circle(frame, (int(veh[0]), int(veh[1])), 3, (255, 0, 255))
            cv2.imshow("image", frame)
            cv2.waitKey(10000)


    else:

        frame = cv2.imread("./frame.jpg")
        collect_vehicles = pickle.load(open("./heatmap_data/collect_vehicles_3.dat","rb"))

        # confidence_score(collect_vehicles)
        binary_heatmap_centroid= create_heatmap(collect_vehicles,frame)
        blob_detection(binary_heatmap_centroid)
        break
        # get heatmap based on bounding box covering area, centriods.

        #generate ROI and lane centers based on heatmap

