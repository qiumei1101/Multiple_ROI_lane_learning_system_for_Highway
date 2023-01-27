import cv2
import os.path
from pathlib import Path
import numpy as np
from datetime import datetime
import time
from Vehicle_Detection import Vehicle_Detection_in_continuous_learning
from Cycle_Learning_multiple_ROI import Cycle_learning_multiple_ROI
from Cycle_Learning_multiple_ROI import Display_Cycle_learning_multiple_ROI
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--video_path', default='/media/meiqiu/CA8C57E38C57C919/MEIREQUESTEDVIDEOS/sunny/'
                                            '1-065-115-5-1+2020-09-05+14.42.mp4', help='camera ip or local video path')
parser.add_argument('--saving_path', default='/home/meiqiu@ads.iu.edu/JTRP_project/Multiple ROI and Lane Learning System/'
                                             '/results/',
                    help='path to save results')
parser.add_argument('--detector', type=str, default='YOLO_v7', choices=['YOLO_v3', 'YOLO_v4','YOLO_v5','YOLO_v7'])
parser.add_argument('--T', type=int, default=60, help='Time interval of each cycle, the unit is second')
parser.add_argument('--conf_thre', type=float, default='0.25', help='Detection confidence score threshold when creating '
                                                                    'the road segment')
parser.add_argument('--lambda_thre', type=int, default='120', help='Criteria of stopping the cycle learning')
args = parser.parse_args()
print(args)

# **************************************** Load Video, Set Saving Path, Set Local & Global Variables ****************************************
video_path = args.video_path
video = cv2.VideoCapture(video_path)
fps = video.get(cv2.CAP_PROP_FPS)
file_name_ = Path(video_path).stem
saving_path = args.saving_path
filepath = os.path.join(saving_path, file_name_)
if not os.path.exists(filepath):
    os.mkdir(filepath)
os.system("clear")
print("filepath",filepath)
'''Define global variables for cycle learning'''
vehicle_collected = False
collect_cars = []
collect_det_dots_including_truck = []
learning_cycle = 0
clyle_learning_period = args.T# 60 seocnds
detector = args.detector
global classifier
if detector == 'YOLO_v7':
    import YOLO_v7 as YOLOV7
    classifier = YOLOV7.YOLO_darknet()
elif detector == 'YOLO_v3':
    import YOLO_v3 as YOLOV3
    classifier = YOLOV3.YOLO_darknet()
elif detector == 'YOLO_v4':
     import YOLO_v4 as YOLOV4
     classifier = YOLOV4.YOLO_darknet()
else:
    import YOLO_v5 as YOLOV5
    classifier = YOLOV5.YOLO_darknet()
# ****************************************Cycle learning starts here!!!!!!!! ****************************************
times_start = time.time()
count = 0
lambda_thres = args.lambda_thre
while (time.time() - times_start < clyle_learning_period):
    # Vehicle Detection with yolo
    collect_det_dots_including_truck, collect_cars, frame = Vehicle_Detection_in_continuous_learning(
        video,classifier, collect_det_dots_including_truck,
        collect_cars, vehicle_collected, count)

    now = datetime.now()
    if (type(frame) is np.ndarray):
        cv2.imshow('Video Detection during Cycle Learning', frame)
        key = cv2.waitKey(1)

    count += 1
    global left_lane_nums, right_lane_nums
    left_lane_nums = 0
    right_lane_nums = 0
    if time.time() - times_start >= clyle_learning_period:
        vehicle_collected = True
        learning_cycle += 1
    if vehicle_collected:  # Finish the current cycle vehicle accumulation!
        if learning_cycle == 1:  # Save figures of debug purpose;
            filename = os.path.join(filepath,
                                    "before first cycle learning" + ".png")
            if (type(frame) is np.ndarray):
                cv2.imwrite(filename, frame)
        else:
            filename = os.path.join(filepath, "Frame_after_the_last_cycle.png")
            if (type(frame) is np.ndarray):
                cv2.imwrite(filename, frame)

        '''Cycle learning to get ROI, baseline, lane centers, lane directions, and road status'''
        if (type(frame) is np.ndarray):
            lane_learning_in_multiple_ROI, road_status_report, lane_annotations, global_lane_centers,\
            ROIs, all_lane_centers_x, ROI_index_list, global_lane_boundarises, lines = Cycle_learning_multiple_ROI(
                collect_det_dots_including_truck, frame, filepath, learning_cycle,lambda_thres)

            left_lane_nums = len([i for i in lane_annotations if i < 0])
            right_lane_nums = len([i for i in lane_annotations if i > 0])


            Display_Cycle_learning_multiple_ROI(collect_det_dots_including_truck,lane_learning_in_multiple_ROI, frame,
                                                filepath, learning_cycle, lane_annotations,
                                                global_lane_centers, all_lane_centers_x)
        '''Cycle learning stops when both the two sides reach to 'M' status, or one road side has no lane detected
         and the other side is in 'M' status;'''
        if road_status_report['left']['status'] == 'M' and road_status_report['right']['status'] == 'M' or \
                road_status_report['left']['status'] == 'M' and right_lane_nums == 0 or road_status_report['right'][
            'status'] == 'M' and left_lane_nums == 0:

            print("cyc learning finish")
            break
        else:
            vehicle_collected = False
            times_start = time.time()
            continue


