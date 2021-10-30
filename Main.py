import time
from vehicle_detection import Vehicle_Detection_in_continuous_learning
import cv2
times_start = time.time()
count = 0
vehicle_collected=False

while (time.time() - times_start < 240):

    collect_vehicles, collect_cars, frame, camera_angle_changed_ELS = Vehicle_Detection_in_continuous_learning(
        vehicle_collected, count)
    count += 1
    lane_status = []
    lane_direction = []
    colors = [(255, 255, 0), (0, 255, 0), (255, 0, 0), (128, 128, 0), (255, 128, 255),
              (0, 0, 255), (128, 0, 128),
              (255, 128, 128), (100, 150, 220), (240, 230, 255)]
    left_group = []
    right_group = []
    left_status = []
    right_status = []
    if time.time() - times_start >= 240:
        vehicle_collected = True

    if vehicle_collected:
        # print("vehicles",collect_vehicles)
        # Get_roi_from_cf(collect_vehicles,frame)
        current_time = time.time()
        for veh in collect_vehicles:
            cv2.circle(frame, (int(veh[0]), int(veh[1])), 3, (255, 0, 255))
        cv2.imshow("image",frame)
        cv2.waitKey(1000)
        # get heatmap based on bounding box covering area, centriods.

        #generate ROI and lane centers based on heatmap

