import cv2
import time
import numpy as np
import os
from Create_Heatmap import create_binary_image
from Multiple_ROI_Baseline_finding import generate_ROI_baseline
from Lane_Finding_multiple_ROI import lane_finding_engine
from Generate_Valid_Road_Map_Ccontours import generate_contour
from Create_Lane_Center_Table import lane_center_table_engine
from Generate_Lane_Boundaries_multiple_ROI import lane_boundaries_engine
from Lane_Fitting_Equations_multiple_ROI import  lane_fitting_engine
from Lane_Direction_multiple_ROI import lane_directions_engine
import Group_Vehicle_Points_To_Lane_multiple_ROI
from heleper import check_execution_time
from heleper import plot_LaneCenters_onFrame
from heleper import Group_Vehicle_near_baseline_multiple_ROI
def Cycle_learning_multiple_ROI(collect_cars,frame,filepath,learning_cycle,lambda_thres):
    """
      Function:  Cycle_learning_multiple_ROI
      --------------------
      implement cycle learning in multiple ROIs, in each ROI;
      In each cycle, finish vehicle detection, valid road segments determination, baseline and ROI determination,
      lane center finding, data grouping, lane curve fitting, lane direction, annotation and boundary detection
        collect_cars: accumulated cars' data till now
        frame: current input video frame
        filepath: saving folder path
        learning_cycle: the index of lane learning time, ex: if learning_cycle=2 means
        it is the second time learning
        lambda_thres: threshold of vehicle number to stop cycle learning
       returns: lane_learning_in_multiple_ROI,road_status_report,lane_annotations,left_lane_centers+right_lane_centers,
       ROIs,\
           all_lane_centers_x,left_lane_ROI_index+right_lane_ROI_index,global_lane_boundarises,lines
    """
    current_time=time.time()
    ''' Generate a binary Image with detected Vehicles'''
    binary_heatmap_area, remain_vehicles = create_binary_image(learning_cycle,collect_cars, frame, filepath)
    ''' Generate several valid Road Segment Contours'''

    remain_cnts = generate_contour(learning_cycle,binary_heatmap_area, frame, filepath)

    current_time = check_execution_time("generate road map contour"+str(learning_cycle), current_time,filepath)

    frame, baseline_and_ROI,cnts = generate_ROI_baseline(learning_cycle,remain_cnts, frame, remain_vehicles,
                                                                    filepath)

    ''' Generate ROI and Baseline in each Road Segment'''
    current_time =check_execution_time("generate roi baseline" + str(learning_cycle),
                                                                  current_time,filepath)

    ''' Lane Center Detection in each ROI'''
    lane_centers = []
    lane_centers = lane_finding_engine(frame,learning_cycle,remain_vehicles,cnts, baseline_and_ROI, lane_centers,
                                       filepath)

    current_time = check_execution_time("generate lane center" + str(learning_cycle),
                                                                  current_time,filepath)
    del_cen = []
    for i in range(len(lane_centers) - 1):
        del_flag = False
        j = i + 1
        while (j < len(lane_centers)):
            if abs(lane_centers[i][0] - lane_centers[j][0]) < 30 and abs(lane_centers[i][1] - lane_centers[j][1]) < 50:
                del_flag = True
            j += 1
        if del_flag:
            del_cen.append(lane_centers[i])
    for lane in del_cen:
        lane_centers.remove(lane)
    lane_centers_cp = lane_centers
    h, w = frame.shape[:2]
    all_up_bound = []
    all_down_bound = []


    for item in baseline_and_ROI:
        all_up_bound.append(item[3])
        all_down_bound.append(item[4])
    if len(all_up_bound) > 0 and len(all_down_bound) > 0:
        del_data = [i for i, x in enumerate(remain_vehicles) if
                    (x[1] < np.min(all_up_bound) or x[1] > np.max(all_down_bound))]

        updated_del_data = []
        for index in del_data:
            for i in range(6):
                updated_del_data.append(index * 6 + i)
        remain_vehicles = np.delete(remain_vehicles, updated_del_data)
        remain_vehicles = remain_vehicles.reshape(int(len(remain_vehicles) / 6), 6)
        remain_vehicles = remain_vehicles.tolist()
    all_lane_centers = []

    baseline_index = 0
    keyes = list(range(len(baseline_and_ROI)))
    '''Initialize the road status data structure; Set the road status of both side to 'N' at the beginning.'''
    road_status_report = {}
    road_status_report = road_status_report.fromkeys(['left', 'right'])
    for key in road_status_report.keys():
        road_status_report[key] = {}
        road_status_report[key].fromkeys(['lane direction', 'lane_centers', 'status'])
        road_status_report[key]['lane direction'] = ' '
        road_status_report[key]['lane_centers'] = []
        road_status_report[key]['status'] = 'N'
    kys=['ROI index', 'baseline_and_roi', 'lane center', 'lane direction', 'groupped data', 'road equations',
       'pixel_relation_in_y']
    lane_learning_in_multiple_ROI = dict(zip(keyes, [None] * len(keyes)))
    for key in keyes:
        lane_learning_in_multiple_ROI[key]=dict(zip(kys, [None] * len(kys)))

    ''' Data grouping, Lane Curving Fitting, Lane Direction Detection and Road Status Checking in each ROI'''
    left_lane_centers=[]
    right_lane_centers=[]
    left_roi=[]
    right_roi=[]
    left_grouped_vehicles = []
    right_grouped_vehicles = []
    left_lane_boundaries = []
    right_lane_boundaries = []
    ROIs = []
    all_lane_centers_x=[]
    left_lane_ROI_index = []
    right_lane_ROI_index =[]
    lines =[]
    time_for_lane_grouping = 0
    time_for_lane_fitting = 0
    time_for_lane_direction = 0
    time_for_lane_boundary = 0

    for item in baseline_and_ROI:
        lane_center = []
        lane_center_for_status = []
        for lane in lane_centers_cp:
            if lane[-1] == baseline_and_ROI.index(item):
                lane_center.append(lane[0])
                all_lane_centers.append(lane[0])
                lane_center_for_status.append((lane[0],item[2]))
        roi_up = int((item[2] - item[3]))
        roi_down = int((item[4] - item[2]))
        ROIs.append([item[2],item[2]-roi_up,item[2]+roi_down,item[0],item[1]])
        current_time=time.time()

        ###########group vehicles to each lane in the ROI
        LCx = Group_Vehicle_Points_To_Lane_multiple_ROI.group_points_engine_weaving(remain_vehicles, item[2], lane_center,
                                                                            roi_up, roi_down, item[0], item[1],5, w,cnts)
        # LCx = Group_Vehicle_Points_To_Lane_multiple_ROI.group_points_engine(remain_vehicles, item[2], lane_center,
        #                                                                     roi_up, roi_down,item[0],item[1],w)
        t1= time.time()-current_time
        time_for_lane_grouping+=t1

        current_time =check_execution_time("grouping" + str(learning_cycle)+'_'+str(baseline_index),
                                                                      current_time,filepath)

        ############lane curve fitting based on the grouped vehicles in the ROI
        road_fitting_equations, dots_for_alllanes, median_width_height_each_y = lane_fitting_engine(
            LCx, lane_center, item[2], roi_up, roi_down, h)
        t2 = time.time() - current_time
        time_for_lane_fitting += t2

        current_time = check_execution_time(
                "lanefitting" + str(learning_cycle) + '_' + str(baseline_index),
                current_time,filepath)

        ############generate lane direction of each lane in the ROI
        lane_directions, avgerage_veh_per_frame, grouped_data_frameid_each_lane = lane_directions_engine(
            dots_for_alllanes, median_width_height_each_y, item[2], lane_center, roi_up,
            roi_down)
        t3 = time.time() - current_time
        time_for_lane_direction += t3

        current_time = check_execution_time(
                "lanedirection" + str(learning_cycle) + '_' + str(baseline_index),
                current_time,filepath)

        grouped_vehicles_near_baseline = Group_Vehicle_near_baseline_multiple_ROI(remain_vehicles, lane_center,
                                                                     item[2], median_width_height_each_y)
        lane_center_table = lane_center_table_engine(h, road_fitting_equations)
        current_time=time.time()

        ############generate lane boundary of each lane in the ROI
        lane_boundaries = lane_boundaries_engine(lane_center_table, lane_center,
                                                 median_width_height_each_y,w)

        t4 = time.time() - current_time
        time_for_lane_boundary += t4

        current_time = check_execution_time(
                "laneboundary" + str(learning_cycle) + '_' + str(baseline_index),
                current_time,filepath)


        if len(lane_directions)>0:
            if lane_directions[0]>0:
                left_roi.append((item[2],item[2]-roi_up,item[2]+roi_down,item[0],item[1]))
            else:
                right_roi.append((item[2],item[2]-roi_up,item[2]+roi_down,item[0],item[1]))

        for lane in lane_center:
            key_list = lane_boundaries[lane].keys()
            key_list = list(key_list)

            if lane_boundaries[lane][key_list[0]]['left_boundary_x']!=None and \
                    lane_boundaries[lane][key_list[-1]]['left_boundary_x']!=None:
                lines.append([lane_boundaries[lane][key_list[0]]['left_boundary_x'],key_list[0],
                              lane_boundaries[lane][key_list[-1]]['left_boundary_x'],key_list[-1]])
            if lane_boundaries[lane][key_list[0]]['right_boundary_x']!=None and \
                    lane_boundaries[lane][key_list[-1]]['right_boundary_x']!=None:
                lines.append([lane_boundaries[lane][key_list[0]]['right_boundary_x'], key_list[0],
                              lane_boundaries[lane][key_list[-1]]['right_boundary_x'], key_list[-1]])

            if len(lane_directions) > 0:
                if lane_directions[lane_center.index(lane)] > 0:
                    left_lane_centers.append(((lane, item[2])))
                    left_lane_boundaries.append(lane_boundaries[lane])
                    left_grouped_vehicles.append(len(grouped_vehicles_near_baseline[lane]))
                    left_lane_ROI_index.append(baseline_index)
                else:
                    right_lane_centers.append(((lane, item[2])))
                    right_lane_boundaries.append(lane_boundaries[lane])
                    right_grouped_vehicles.append(len(grouped_vehicles_near_baseline[lane]))
                    right_lane_ROI_index.append(baseline_index)

        lane_learning_in_multiple_ROI[baseline_index]['ROI index']=baseline_index
        lane_learning_in_multiple_ROI[baseline_index]['baseline_and_roi']=[item[0],item[1],item[2],item[3], item[4]]
        lane_learning_in_multiple_ROI[baseline_index]['lane center']=lane_center
        lane_learning_in_multiple_ROI[baseline_index]['lane direction']=lane_directions
        lane_learning_in_multiple_ROI[baseline_index]['groupped data']=LCx
        lane_learning_in_multiple_ROI[baseline_index]['road equations']=road_fitting_equations
        lane_learning_in_multiple_ROI[baseline_index]['lane boundaries']=lane_boundaries
        lane_learning_in_multiple_ROI[baseline_index]['pixel_relation_in_y']=median_width_height_each_y
        baseline_index += 1


    ###########check status of each lane
    if len(all_lane_centers) == 0:
        # if no lane detected, set the road status to 'N'
        road_status_report['left']['lane direction'] = ' '
        road_status_report['left']['lane_centers'] = []
        road_status_report['left']['status'] = 'N'
        road_status_report['right']['lane direction'] = ' '
        road_status_report['right']['lane_centers'] = []
        road_status_report['right']['status'] = 'N'
        road_status_report['left']['ROI'] = []
        road_status_report['right']['ROI'] = []
    else:
        road_status_report['left']['lane direction'] = 1
        road_status_report['left']['lane_centers'] = left_lane_centers
        if np.mean(left_grouped_vehicles)>lambda_thres:
          road_status_report['left']['status'] = 'M'
        elif 10 < np.mean(left_grouped_vehicles) < lambda_thres:
          road_status_report['left']['status'] = 'L'
        else:
            road_status_report['left']['status'] = 'N'
        road_status_report['right']['lane direction'] = -1
        road_status_report['right']['lane_centers'] = right_lane_centers


        if np.mean(right_grouped_vehicles) > lambda_thres:
            road_status_report['right']['status'] = 'M'
        elif 10 < np.mean(right_grouped_vehicles) <lambda_thres:
            road_status_report['right']['status'] = 'L'
        else:
            road_status_report['right']['status'] = 'N'

        road_status_report['left']['ROI'] = left_roi
        road_status_report['right']['ROI'] = right_roi
    lane_annotations=[]
    if len(left_lane_centers)==0:
        if len(right_lane_centers)>0:
                for i in range(len(right_lane_centers)):
                    lane_annotations.append(i+1)
    else:
        if len(right_lane_centers)==0:
            for i in range(len(left_lane_centers)):
                lane_annotations.append((len(left_lane_centers)-i)*-1)
        else:
            for i in range(len(left_lane_centers)):
                lane_annotations.append((len(left_lane_centers)-i)*-1)
            for i in range(len(right_lane_centers)):
                lane_annotations.append(i + 1)

    #############organize lane learning results based ROI order from left to right of the frame
    lane_boundaries_=left_lane_boundaries+right_lane_boundaries
    global_lane_boundarises = {}
    global_lane_boundarises = global_lane_boundarises.fromkeys(lane_annotations, [])
    for ann in lane_annotations:
        global_lane_boundarises[ann]=lane_boundaries_[lane_annotations.index(ann)]
    for lane in left_lane_centers:
        all_lane_centers_x.append(lane[0])
    for lane in right_lane_centers:
        all_lane_centers_x.append(lane[0])
    execution_time_string = "Execution Time for " + "total lane grouping" + ": " +\
                            str(round(time_for_lane_grouping, 3)) + "\n"
    filename = os.path.join(filepath, "Execution_time.txt")
    with open(filename, "a+") as file:
        file.write(execution_time_string)
        file.close()
    execution_time_string = "Execution Time for " + "total lane fitting" + ": " + str(
        round(time_for_lane_fitting, 3)) + "\n"

    filename = os.path.join(filepath, "Execution_time.txt")
    with open(filename, "a+") as file:
        file.write(execution_time_string)
        file.close()
    execution_time_string = "Execution Time for " + "total lane direction" + ": " + str(
        round(time_for_lane_direction, 3)) + "\n"

    filename = os.path.join(filepath, "Execution_time.txt")
    with open(filename, "a+") as file:
        file.write(execution_time_string)
        file.close()

    execution_time_string = "Execution Time for " + "total lane boundary" + ": " + str(
        round(time_for_lane_boundary, 3)) + "\n"

    filename = os.path.join(filepath, "Execution_time.txt")
    with open(filename, "a+") as file:
        file.write(execution_time_string)
        file.close()
    return lane_learning_in_multiple_ROI,road_status_report,lane_annotations,left_lane_centers+right_lane_centers,ROIs,\
           all_lane_centers_x,left_lane_ROI_index+right_lane_ROI_index,global_lane_boundarises,lines

def Display_Cycle_learning_multiple_ROI(collect_det_dots_including_truck,lane_learning_in_multiple_ROI,
                                        frame, filepath,learing_cycle,lane_annotations,global_lane_centers,
                                        all_lane_centers_x):
    """
      Function:  Display_Cycle_learning_multiple_ROI
      --------------------
        draw the results on the frame after each cycle finishes
    """
    if learing_cycle==1:
        filename = os.path.join(filepath, "before first cycle learning.png")
    else:
        filename = os.path.join(filepath, "Frame_after_the_last_cycle.png")
    frame5 = cv2.imread(filename)
    frame1 = cv2.imread(filename)
    frame2 = cv2.imread(filename)
    frame3 = cv2.imread(filename)
    frame4 = cv2.imread(os.path.join(filepath,str(learing_cycle)+'_'+'contour_on_roadmap.png'))
    for box in collect_det_dots_including_truck:
       cv2.circle(frame5,(int(box[0]),int(box[1])),3,(255,0,255),2)
    for item in lane_learning_in_multiple_ROI.keys():
        #         # draw the grouped data
        colors = [(255, 255, 0), (0, 255, 0), (255, 0, 0), (128, 128, 0), (128, 0, 255),
                  (0, 0, 255), (128, 0, 128),
                  (255, 128, 128), (100, 150, 220), (240, 230, 255), (0, 0, 125), (120, 0, 0), (20, 50, 100),
                  (100, 20, 128), (30, 40, 60), (100, 40, 70), (80, 70, 60)]
        LCx = lane_learning_in_multiple_ROI[item]['groupped data']
        lane_center = lane_learning_in_multiple_ROI[item]['lane center']
        road_fitting_equations = lane_learning_in_multiple_ROI[item]['road equations']
        lane_directions = lane_learning_in_multiple_ROI[item]['lane direction']
        median_width_height_each_y = lane_learning_in_multiple_ROI[item]['pixel_relation_in_y']
        lane_boundaries = lane_learning_in_multiple_ROI[item]['lane boundaries']
        baseline_and_ROI = lane_learning_in_multiple_ROI[item]['baseline_and_roi']
        roi_up = int((baseline_and_ROI[2] - baseline_and_ROI[3]))
        roi_down = int((baseline_and_ROI[4] - baseline_and_ROI[2]))

        for key in list(LCx.keys()):
            for lane in lane_center:
                if LCx[key][lane] != [] and LCx[key][lane]['datapoints'] != []:
                    for point in LCx[key][lane]['datapoints']:
                        cv2.circle(frame5, (int(point[0]), int(point[1])), 3, colors[all_lane_centers_x.index(lane)], 2)

        for key in list(road_fitting_equations.keys()):
            if len(road_fitting_equations[key]) != 0:
                coef = road_fitting_equations[key][0]
                poly1d_fn = np.poly1d(coef)
                pts_y = range(baseline_and_ROI[2] - int(roi_up), baseline_and_ROI[2] + int(roi_down))
                pts_x = poly1d_fn(pts_y)
                for m in range(len(pts_y)):
                    cv2.circle(frame1, (int(pts_x[m]), int(pts_y[m])), 2, (255, 255, 0), 2)
                    cv2.circle(frame, (int(pts_x[m]), int(pts_y[m])), 2, (255, 255, 0), 2)
        for lane in lane_center:
            for y in list(median_width_height_each_y[lane].keys()):
                if not np.isnan(lane_boundaries[lane][y]['left_boundary_x']):
                    cv2.circle(frame2, (int(lane_boundaries[lane][y]['left_boundary_x']), y), 2,
                               (127, 0, 255), 2)
                    cv2.circle(frame, (int(lane_boundaries[lane][y]['left_boundary_x']), y), 2,
                               (127, 0, 255), 2)
            # #
            for y in list(median_width_height_each_y[lane].keys()):
                if not np.isnan(lane_boundaries[lane][y]['right_boundary_x']):
                    cv2.circle(frame2, (int(lane_boundaries[lane][y]['right_boundary_x']), y),
                               2, (127, 0, 255),
                               2)
                    cv2.circle(frame, (int(lane_boundaries[lane][y]['right_boundary_x']), y),
                               2, (127, 0, 255),
                               2)
        for lane in lane_learning_in_multiple_ROI[item]['lane center']:
            cv2.circle(frame3, (int(lane), int(baseline_and_ROI[2])), 6, (0, 0, 255), 7)
            cv2.circle(frame, (int(lane), int(baseline_and_ROI[2])), 6, (0, 0, 255), 7)

        cv2.rectangle(frame4, (baseline_and_ROI[0], baseline_and_ROI[3]), (baseline_and_ROI[1],
                                                                           baseline_and_ROI[4]), (0, 255, 0), 3)
        cv2.line(frame4, (baseline_and_ROI[0], baseline_and_ROI[2]), (baseline_and_ROI[1],
                                                                      baseline_and_ROI[2]), (0, 255, 255), 4)
        for lane in lane_center:
            cv2.circle(frame4, (int(lane), int(baseline_and_ROI[2])), 10, (0, 0, 255), -1)

        frame3 = plot_LaneCenters_onFrame(frame3, baseline_and_ROI[2],
                                         lane_center,
                                         lane_directions)
        frame = plot_LaneCenters_onFrame(frame, baseline_and_ROI[2],
                                          lane_center,
                                          lane_directions)
        # draw lane annotation
    for ann in lane_annotations:
        cv2.putText(frame, str(ann),
                    (global_lane_centers[lane_annotations.index(ann)][0],
                     global_lane_centers[lane_annotations.index(ann)][1] - 5), 0, 1,
                        (0, 0, 0),
                        2)

    file_name = str(learing_cycle) + '_' + 'lane_fitting.png'
    cv2.imwrite(os.path.join(filepath, file_name), frame1)
    file_name = str(learing_cycle) + '_' + 'lane_boundary.png'
    cv2.imwrite(os.path.join(filepath, file_name), frame2)
    file_name = str(learing_cycle) + '_' + 'lane_cen_dir.png'
    cv2.imwrite(os.path.join(filepath, file_name), frame3)
    file_name = str(learing_cycle)+'_'+'lane_learning_in_multiple_ROI.png'
    cv2.imwrite(os.path.join(filepath,file_name), frame)

    file_name = str(learing_cycle) + '_' + 'lane_finding.png'
    cv2.imwrite(os.path.join(filepath, file_name), frame4)
    file_name = str(learing_cycle) + '_' + 'lane_grouping.png'
    cv2.imwrite(os.path.join(filepath, file_name), frame5)

