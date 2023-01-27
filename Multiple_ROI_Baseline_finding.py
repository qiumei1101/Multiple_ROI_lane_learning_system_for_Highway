import cv2
import os
import numpy as np
import  matplotlib.pyplot as plt
from joblib import Parallel, delayed
def findlane_intersect(i,data_inputs):
    blank_mask = np.zeros((data_inputs[0], data_inputs[1], 3), np.uint8)
    cv2.drawContours(blank_mask, data_inputs[2], -1, (0, 255, 0), 1)
    contours_idx = blank_mask[..., 1] == 255
    line_baseline = [0, i, data_inputs[1], i]
    cv2.line(blank_mask, (line_baseline[0], line_baseline[1]), (line_baseline[2], line_baseline[3]),
             (255, 0, 0), thickness=1)
    lines_idx = blank_mask[..., 0] == 255
    overlap = np.where(contours_idx * lines_idx)
    return overlap
def generate_ROI_baseline(learning_cycle,remain_cnts,frame,remain_vehicles,filepath):

    contours_centers=[]
    baseline_and_ROI =[]
    index = 0
    h0,w0=frame.shape[:2]
    road_bound=[]
    for c in remain_cnts:
            vehicles_in_road=[]
            conf_in_road=[]
            vehicle_height=[]
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            contours_centers.append((cX,cY))
            leftmost = tuple(c[c[:, :, 0].argmin()][0])
            rightmost = tuple(c[c[:, :, 0].argmax()][0])
            topmost = tuple(c[c[:, :, 1].argmin()][0])
            bottommost = tuple(c[c[:, :, 1].argmax()][0])
            h = range(topmost[1],bottommost[1])
            conf_y = {}
            conf_y = conf_y.fromkeys(h,[])
            num_y = {}
            num_y = num_y.fromkeys(h,0)
            conf_list=[]
            count_list=[]
            h_index=[]
            for i in h:
                conf_y[i]=[]
                num_y[i]=0
            for veh in remain_vehicles:
                if veh[0]-veh[2]>leftmost[0] and veh[0]+veh[2]<rightmost[0] and veh[1]-veh[3]>topmost[1] and veh[1]+veh[3]<bottommost[1]:
                    vehicles_in_road.append(veh)
                    conf_in_road.append(veh[-1])
                    vehicle_height.append(veh[3])
                    h_index.append(veh[1])
                    conf_y[veh[1]].append(veh[-1])
                    num_y[veh[1]]+=1

            position_list = []
            above_cY_position_list =[]
            above_cY_conf_list=[]
            above_cY_count_list=[]
            for i in h:
                if len(conf_y[i]) > 0:
                    position_list.append(i)
                    conf_list.append(np.mean(conf_y[i]))
                    count_list.append(num_y[i])
                if len(conf_y[i]) > 0 and i>cY:
                    above_cY_position_list.append(i)
                    above_cY_conf_list.append(np.mean(conf_y[i]))
                    above_cY_count_list.append(num_y[i])

            if len(conf_list)>0 and len(above_cY_count_list)>0 and len(above_cY_conf_list)>0:
                max_value = max(np.array(above_cY_count_list) * np.array(above_cY_conf_list))
                max_index = list(np.array(above_cY_count_list) * np.array(above_cY_conf_list)).index(max_value)
                baseline = above_cY_position_list[max_index]
                roi_down = baseline+ 4.5*np.median(vehicle_height)
                roi_up = baseline -4.5*np.median(vehicle_height)
                if roi_down > bottommost[1]:
                    roi_down = bottommost[1]
                if roi_up<topmost[1]:
                    roi_up = topmost[1]

                roi_up = int(roi_up)
                roi_down = int(roi_down)
                baseline = int((roi_down+roi_up)/2)

                boundary_dict = {}
                boundary_dict = boundary_dict.fromkeys(range(roi_up, roi_down+1))
                data_inputs = [h0, w0, c,boundary_dict]
                overlap=Parallel(n_jobs=-1)(delayed(findlane_intersect)(i, data_inputs) for i in range(roi_up,roi_down+1))
                for i in range(roi_up,roi_down+1):
                    boundary_dict[i] = {}
                    boundary_dict[i]=boundary_dict[i].fromkeys(['left_x','left_y','right_x','right_y'],0)
                    left_x = []
                    left_y = []
                    right_x = []
                    right_y = []
                    if len(list(list(zip(*overlap))[1][i-roi_up]))>0:
                        for cen in list(list(zip(*overlap))[1][i-roi_up]):
                            if cen < cX:
                                left_x.append(cen)
                                left_y.append(i)
                            else:
                                right_x.append(cen)
                                right_y.append(i)
                    if len(left_x)!=0:
                        boundary_dict[i]['left_x']=np.min(left_x)
                        boundary_dict[i]['left_y']=i
                    if len(right_x)!=0:
                        boundary_dict[i]['right_x']=np.max(right_x)
                        boundary_dict[i]['right_y']=i
                plt.rcParams['font.size'] = '12'
                plt.rcParams["font.weight"] = "bold"
                plt.rcParams["axes.labelweight"] = "bold"

                if learning_cycle==2 and index==2:
                    ax = plt.gca()
                    ax.plot(position_list, np.array(count_list) * np.array(conf_list), color='k')
                    y_range_2 = ax.get_ylim()
                    ax.set_ylabel("Avg Conf*Count")
                    plt.vlines(cY-20, y_range_2[0], y_range_2[1], colors='k')
                    plt.text(cY-20, 1 / 3 * (y_range_2[1] - y_range_2[0])-5, 'cY',fontsize=10)
                    plt.vlines(roi_down, y_range_2[0], y_range_2[1], colors='m')
                    plt.text(roi_down+3, 1 / 3 * (y_range_2[1] - y_range_2[0])-10, 'ROI\ndown',fontsize=10)
                    plt.vlines(roi_up, y_range_2[0], y_range_2[1], colors='c')
                    plt.text(roi_up+3, 1 / 3 * (y_range_2[1] - y_range_2[0])+10, 'ROI\nup',fontsize=10)
                    plt.vlines(baseline, y_range_2[0], y_range_2[1], colors='r')
                    plt.text(baseline+5, 1/ 3 * (y_range_2[1] - y_range_2[0])+15, 'baseline',fontsize=10)
                    plt.xlabel("Pixel Position at Y axis")
                    save_name = os.path.join(filepath, str(learning_cycle)+'_'+str(index)+'_'+"conf_count.png")
                    plt.savefig(save_name)
                x_boundary_list_left = []
                valid_list_left =[]
                all_x_boundary_list_left =[]
                valid_list_right =[]
                x_boundary_list_right = []
                all_x_boundary_list_right = []
                for key in list(boundary_dict.keys()):
                    if boundary_dict[key]['left_y']==0:
                        boundary_dict[key]['left_y']=key
                    if boundary_dict[key]['right_y']==0:
                        boundary_dict[key]['right_y']=key
                    all_x_boundary_list_left.append(boundary_dict[key]['left_x'])
                    all_x_boundary_list_right.append(boundary_dict[key]['right_x'])
                    if boundary_dict[key]['left_x']!=0:
                       x_boundary_list_left.append(boundary_dict[key]['left_x'])
                       valid_list_left.append(key)
                    if boundary_dict[key]['right_x']!=0:
                        x_boundary_list_right.append(boundary_dict[key]['right_x'])
                        valid_list_right.append(key)
                index+=1
                if len(x_boundary_list_left)>0 and len(x_boundary_list_right)>0:
                      baseline_and_ROI.append((int(np.min(x_boundary_list_left)),int(np.max(x_boundary_list_right)),baseline,roi_up,roi_down,cX))
                else:
                    baseline_and_ROI = []
                road_bound.append(boundary_dict)
    global cnts
    cnts = None
    if baseline_and_ROI!=[] and remain_cnts!=None:
         baseline_and_ROI,cnts = zip(*sorted(zip(baseline_and_ROI, remain_cnts),key=lambda x: int(x[0][0])))
    for item in baseline_and_ROI:
        cv2.rectangle(frame,(item[0],item[3]),(item[1],item[4]),(0,255,0),3)
        cv2.line(frame, (item[0],item[2]),(item[1],item[2]), (0, 255, 255), 4)
    cv2.imwrite(os.path.join(filepath, str(learning_cycle)+'_'+'ROI_baseline.png'), frame)

    return frame, baseline_and_ROI,road_bound,cnts