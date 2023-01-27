
from itertools import groupby
import numpy as np

def lane_directions_engine(LCx, median_width_height_each_y, baseline, lane_centers, roi_up, roi_down):
    """
      Function:  lane_directions_and_annotation_engine
      --------------------
      generate lane direction and annotation of each lane

        LCx: grouped vehicles in all the lanes, which is generated by the file
        Group_Vehicle_Points_To_Lane_multiple_ROI.py
        median_width_height_each_y: estimated car's median width and height in current ROI
        baseline: reference line in the ROI
        lane_centers: lane center positions at the baseline in the ROI
        roi_up: up boundary of the ROI
        roi_down: bottom boundary of the ROI
       returns: lane_directions,avgerage_veh_per_frame,grouped_data_frameid_each_lane

        notes: we only generate two moving directions: -1 means moving close to the camera,
        +1 means moving away from the camera
    """
    lane_directions = []
    sorted_data_with_frame_d={}
    sorted_data_with_frame_d.fromkeys(list(LCx.keys()),[])
    for key in list(LCx.keys()):
        sorted_data_with_frame_d[key]=[]
        px = []
        py = []
        pw = []
        ph = []
        frame_id = []
        for item in LCx[key]:
            px.append(item[0]), py.append(item[1]), pw.append(item[2]), ph.append(item[3]), frame_id.append(item[4])

        px_sorted=[x for _, x in sorted(zip(frame_id, px), key=lambda pair: pair[0])]
        py_sorted = [y for _, y in sorted(zip(frame_id, py), key=lambda pair: pair[0])]
        pw_sorted = [w for _, w in sorted(zip(frame_id, pw), key=lambda pair: pair[0])]
        ph_sorted = [h for _, h in sorted(zip(frame_id, ph), key=lambda pair: pair[0])]
        sorted_data_with_frame_d[key].append(px_sorted)
        sorted_data_with_frame_d[key].append(py_sorted)
        sorted_data_with_frame_d[key].append(pw_sorted)
        sorted_data_with_frame_d[key].append(ph_sorted)
        sorted_data_with_frame_d[key].append(sorted(frame_id))
    distance_each_y = {}
    distance_each_y = distance_each_y.fromkeys(lane_centers)
    for k in list(distance_each_y.keys()):
        distance_each_y[k] = {}
        distance_each_y[k].fromkeys(range(baseline - roi_up-20, baseline + roi_down+2+1))

        for kk in range(baseline - roi_up-20,baseline + roi_down+20+1):

            distance_each_y[k][kk] = {}
            distance_each_y[k][kk].fromkeys(['tracked number','distance y'])
            distance_each_y[k][kk]['tracked number'] = 0
            distance_each_y[k][kk]['distance y'] = []

    avgerage_veh_per_frame = []
    grouped_data_frameid_each_lane = []
    for k in list(LCx.keys()):

        grouped_frame_id = [list(j) for i, j in groupby(sorted_data_with_frame_d[k][-1])]
        grouped_px_sorted = []
        grouped_py_sorted = []
        grouped_pw_sorted = []
        grouped_ph_sorted = []

        n = 0
        for kk in range(len(grouped_frame_id)):
            x = []
            y = []
            w = []
            h = []

            for j in range(len(grouped_frame_id[kk])):
                x.append(sorted_data_with_frame_d[k][0][n + j])
                y.append(sorted_data_with_frame_d[k][1][n + j])
                w.append(sorted_data_with_frame_d[k][2][n + j])
                h.append(sorted_data_with_frame_d[k][3][n + j])
            grouped_px_sorted.append(x)
            grouped_py_sorted.append(y)
            grouped_pw_sorted.append(w)
            grouped_ph_sorted.append(h)
            n += len(grouped_frame_id[kk])
        if len(grouped_frame_id) == 0:
            avgerage_veh_per_frame.append(0)
            grouped_data_frameid_each_lane.append([])
        else:
            grouped_data_frameid_each_lane.append(
                (grouped_frame_id, grouped_px_sorted, grouped_py_sorted, grouped_pw_sorted, grouped_ph_sorted))
            avgerage_veh_per_frame.append(n / len(grouped_frame_id))
        for kk in range(len(grouped_frame_id)-1):
            for jj in range(len(grouped_frame_id[kk + 1])):
              for kkk in range(len(grouped_frame_id[kk])):

                if k in median_width_height_each_y.keys():
                  if median_width_height_each_y[k][grouped_py_sorted[kk][kkk]]!=[]:
                   if abs(grouped_py_sorted[kk+1][jj]-grouped_py_sorted[kk][kkk])<(1/3)*median_width_height_each_y[k][grouped_py_sorted[kk][kkk]][0][1]:

                        distance_each_y[k][grouped_py_sorted[kk][kkk]]['distance y'].append(grouped_py_sorted[kk+1][jj]-grouped_py_sorted[kk][kkk])
                        distance_each_y[k][grouped_py_sorted[kk][kkk]]['tracked number']+=1

                        kkk+=1
                        continue
        distance_y=[]
        if k in distance_each_y.keys():
            for j in list(distance_each_y[k].keys()):
                distance_y.append(np.sum(distance_each_y[k][j]['distance y']))
        if np.sum(distance_y)>0:
            lane_directions.append(1)
        else:
            lane_directions.append(-1)

    return lane_directions,avgerage_veh_per_frame,grouped_data_frameid_each_lane