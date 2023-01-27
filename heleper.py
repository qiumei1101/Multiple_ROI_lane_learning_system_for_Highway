import os
import time
import cv2
import numpy as np
def check_execution_time(module_name, start_time,filepath):
    """
      Function:  check_execution_time
      --------------------
      computes the system time cost of each module

        module_name: name of each module
        start_time: module starts time
        filepath: time file saving path
       returns: current_time which means current system time
    """
    current_time = time.time()
    execution_time_string = "Execution Time for " + module_name + ": " + str(round(current_time - start_time, 3)) + "\n"
    filename = os.path.join(filepath, "Execution_time.txt")

    with open(filename, "a+") as file:
            file.write(execution_time_string)
            file.close()
    return current_time


def get_FPS(video_link):
    """
      Function:  get_FPS
      --------------------
      get the fps of the input video

       returns: FPS which represents the fps of the video
    """
    video = cv2.VideoCapture(video_link)
    FPS = video.get(cv2.CAP_PROP_FPS)
    video.release()
    return FPS


def plot_baseline_onFrame(frame, baseline):
    """
    Parameters
    ----------
    frame           :(numpy array) frame input
    baseline        :(int) baseline value
    Returns
    -------
    frame           :(numpy array) frame output with baseline drawn
    """
    h, w = frame.shape[:2]
    cv2.line(frame, (0, int(baseline)), (w, int(baseline)), (0, 255, 0), 3)
    return frame


def plot_LaneCenters_onFrame(frame, baseline, lane_centers, lane_directions):

    """
    Parameters
    ----------
    frame           :(numpy array) frame input
    baseline        :(int) baseline value
    lane_centers    :(list) list of lane center x coordinates
    lane_directions :(list) list of lane center directions (+ve => down dir, -ve => up dir
    Returns
    -------
    frame           :(numpy array) frame after applying lane centers with direction to the frame
    """
    for lane in lane_centers:
        cv2.circle(frame, (int(lane), int(baseline)), 10, (0, 0, 255), -1)
    if lane_directions is not None:

        for i, h in enumerate(lane_directions):
            if lane_directions[i]!=0:
                if lane_directions[i] < 0:
                    cv2.drawContours(frame, [np.array(
                        [(lane_centers[i] - 12, baseline),
                         (lane_centers[i] + 12, baseline),
                         (lane_centers[i], baseline - 12)]).astype(int)], 0, (255, 0, 0), -1)
                else:
                    cv2.drawContours(frame, [np.array(
                        [(lane_centers[i] - 12, baseline),
                         (lane_centers[i] + 12, baseline),
                         (lane_centers[i], baseline + 12)]).astype(int)], 0, (255, 0, 0), -1)
    return frame
def Group_Vehicle_near_baseline_multiple_ROI(collect_vehicles,lane_centers,
                                             baseline,median_width_height_each_y):
    grouped_vehicles_near_baseline={}
    grouped_vehicles_near_baseline=grouped_vehicles_near_baseline.fromkeys(lane_centers,[])

    if len(lane_centers)>0:
        if lane_centers[0] in median_width_height_each_y.keys():
            if median_width_height_each_y[lane_centers[0]][baseline]!= [] and np.isnan(median_width_height_each_y[lane_centers[0]][baseline][0][1])==False:
                         checking_range_ = int(median_width_height_each_y[lane_centers[0]][baseline][0][1]/5)
            else:
                 checking_range_ = 10
        for lane in lane_centers:
            grouped_vehicles_near_baseline[lane]=[]
            for veh in collect_vehicles:
                 if veh[1] < baseline + checking_range_*3 and veh[1]  > baseline - checking_range_*3:
                     if baseline in median_width_height_each_y[lane].keys():
                         theshold_=median_width_height_each_y[lane][baseline][0][0]/3
                     else:
                         theshold_=15
                     if abs(lane - veh[0]) <= theshold_:
                         if veh not in grouped_vehicles_near_baseline[lane]:
                             grouped_vehicles_near_baseline[lane].append(veh)
    return grouped_vehicles_near_baseline
#
#
# def Determine_jam(Collected_Vehicle_data,cycle_learning,Median_HW_each_y,baseline,reference_FPS,w,lane):
#     Jam_is_True = False
#     if Collected_Vehicle_data!=[]:
#         max_frame_id = int(Collected_Vehicle_data[-1][4])
#         min_frame_id = int(Collected_Vehicle_data[0][4])
#
#         if max_frame_id - min_frame_id>200:
#             checking_range = 200
#         else:
#             checking_range= max_frame_id - min_frame_id
#         checking_vehicles={}
#         checking_vehicles=checking_vehicles.fromkeys(range(max_frame_id-checking_range,max_frame_id),[])
#         index=0
#
#         for id in checking_vehicles.keys():
#             checking_vehicles[id]=[]
#             for veh in Collected_Vehicle_data[index:]:
#                 if veh[4]==id:
#                     checking_vehicles[id].append(veh)
#                     index+=1
#         y_diff_sum = 0
#         compare_times =0
#         for fid in checking_vehicles.keys():
#             for veh in checking_vehicles[fid]:
#                 if fid+1<max_frame_id and len(checking_vehicles[fid+1])>0:
#                     for veh2 in checking_vehicles[fid+1]:
#                         if Median_HW_each_y!=None and baseline in Median_HW_each_y.keys():
#                             if Median_HW_each_y[baseline]!=[]:
#                                 if abs(veh[0]-veh2[0])<Median_HW_each_y[baseline][0][0]/3:
#                                     y_diff_sum+=abs(veh[1]/veh[3]-veh2[1]/veh2[3])
#                                     compare_times += 1
#                                 # continue
#                         else:
#                             if abs(veh[0] - veh2[0]) < 5:
#                                 y_diff_sum += abs(veh[1] / veh[3] - veh2[1] / veh2[3])
#                                 compare_times += 1
#                 elif fid+2<max_frame_id and len(checking_vehicles[fid+2])>0:
#                     for veh2 in checking_vehicles[fid+2]:
#                         if Median_HW_each_y!=None and baseline in Median_HW_each_y.keys():
#                             if Median_HW_each_y[baseline]!=[]:
#                                 if abs(veh[0]-veh2[0])<Median_HW_each_y[baseline][0][0]/5:
#                                     y_diff_sum += abs(veh[1] / veh[3] - veh2[1] / veh2[3]) / 2
#                                     compare_times += 1
#                         else:
#                             if abs(veh[0]-veh2[0])<10:
#                                 y_diff_sum+=abs(veh[1]/veh[3]-veh2[1]/veh2[3])/2
#                                 compare_times += 1
#                             # continue
#                 else:
#                     continue
#         if compare_times==0:
#             compare_times+=1
#
#         avg_mer_pixel=0
#         threshold_diff = 4.44/reference_FPS
#         if Median_HW_each_y!=None and baseline in Median_HW_each_y.keys():
#             if Median_HW_each_y[baseline]!=[]:
#                 if lane <= w / 2 + 200 and lane >= w / 2 - 200:
#                     avg_mer_pixel = float(8 / Median_HW_each_y[baseline][0][1]) * 3
#             else:
#                 avg_mer_pixel = float(8 / Median_HW_each_y[baseline][0][1]) * 3.5
#
#         else:
#             avg_mer_pixel=0.6
#         if np.isnan(avg_mer_pixel):
#             avg_mer_pixel = 0.6
#
#         if  y_diff_sum / compare_times*avg_mer_pixel<threshold_diff and len(Collected_Vehicle_data)>=300*cycle_learning:
#             Jam_is_True = True
#     return Jam_is_True
#
