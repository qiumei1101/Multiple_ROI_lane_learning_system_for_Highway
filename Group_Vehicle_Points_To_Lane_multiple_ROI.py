def group_points_engine(collect_det_dots,baseline,lane_centers,roi_up,roi_down,roi_left,roi_right,w):
    """
      Function:  group_points_engine
      --------------------
      group vehicle in a ROI to each lane inside of the ROI

        collect_det_dots: all the accumulated vehicles in the ROI till now
        baseline: reference line in the ROI
        lane_centers: lane center positions at the baseline in the ROI
        roi_up: up boundary of the ROI
        roi_down: bottom boundary of the ROI
        roi_left: left boundary of the ROI
        roi_right: right boundary of the ROI
        w: width of the whole frame
       returns: LCx which represents grouped vehicles in all the lanes
    """
    collect_det_dots__=collect_det_dots
    import numpy as np
    del_lane =[]
    for lane in lane_centers:
        if np.abs(lane-w) <=25 or np.abs(lane-0)<=25:
            del_lane.append(lane)
    for lane in del_lane:
        lane_centers.remove(lane)
    roi_up_band = int(roi_up+20)
    roi_down_band = int(roi_down+20)
    dict_save_data_each_y = None

    if dict_save_data_each_y == None:
        dict_save_data_each_y = {}
        k = baseline - roi_up_band
        while(k<baseline+roi_down_band+1):
            dict_save_data_each_y[k] = []
            dict_save_data_each_y[k] = [item for item in collect_det_dots__ if item[1] == k and item[0]>=roi_left and item[0]<=roi_right]

            k+=1

    valid_flag = 'Valid'
    LCx = {}
    LCx = LCx.fromkeys(range(baseline - roi_up_band, baseline + roi_down_band+1))
    k = baseline - roi_up_band
    ##group vehicles in the bottom part of ROI
    while(k<baseline+roi_down_band+1):
        LCx[k] = {}
        LCx[k].fromkeys(lane_centers)
        for kk in lane_centers:
            LCx[k][kk] = {}
            LCx[k][kk].fromkeys(['datapoints', 'center', 'count', 'median_width', 'median_height', 'flag'])
            LCx[k][kk]['datapoints'],LCx[k][kk]['center'],LCx[k][kk]['count'], LCx[k][kk]['median_width'],LCx[k][kk]['median_height'],LCx[k][kk]['flag']= [],kk,0,0,0,valid_flag
        k+=1
    k = baseline+1
    while(k<baseline+roi_down_band+1):
      if k in dict_save_data_each_y.keys():
        a = dict_save_data_each_y[k]
        if a != []:
            a = sorted(a)
        width = []
        height=[]
        for item in a:
            width.append(item[2])
            height.append(item[3])

        for cen in list(LCx[k].keys()):
          if k-1 in LCx.keys() and cen in list(LCx[k-1].keys()):
            del_=[]
            for j in a:
                if abs(j[0] - LCx[k-1][cen]['center']) < np.median(width)*1/4:
                    LCx[k][cen]['datapoints'].append(j)
                    del_.append(j)
            for j in del_:
             a.remove(j)
            if LCx[k][cen]['datapoints'] != []:
                point_x = []
                w=[]
                h=[]
                for point in LCx[k][cen]['datapoints']:
                    point_x.append(point[0])
                    w.append(point[2])
                    h.append(point[3])
                LCx[k][cen]['center'],LCx[k][cen]['median_width'], LCx[k][cen]['median_height'],LCx[k][cen]['count']= np.mean(point_x), np.median(w),np.median(h),len(LCx[k][cen]['datapoints'])
            else:
                    LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                        'count'] = LCx[k-1][cen]['center'], LCx[k-1][cen]['median_width'], LCx[k-1][cen]['median_height'], 0

            if k >= baseline + 3:
                if LCx[k][cen]['count'] == 0 and LCx[k - 1][cen]['count'] == 0 and LCx[k - 2][cen]['count'] == 0:

                        LCx[k][cen]['flag'] = 'inValid'

      k+=1
    ##group vehicles in the up part of ROI
    k = baseline - 1
    while (k >= baseline - roi_up_band):
        a = dict_save_data_each_y[k]
        if a != []:
            a = sorted(a)
        width = []
        height = []
        for item in a:
            width.append(item[2])
            height.append(item[3])

        for cen in list(LCx[k].keys()):
            del_=[]
            for j in a:
                if abs(j[0] - LCx[k + 1][cen]['center']) < np.median(width)*1/5:
                    LCx[k][cen]['datapoints'].append(j)
                    del_.append(j)
            for j in del_:
                a.remove(j)
            if LCx[k][cen]['datapoints'] != []:
                point_x = []
                w=[]
                h=[]
                for point in LCx[k][cen]['datapoints']:
                    point_x.append(point[0])
                    w.append(point[2])
                    h.append(point[3])
                LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                    'count'] = np.mean(point_x), np.median(w), np.median(h), len(LCx[k][cen]['datapoints'])

            else:

                LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                    'count'] = LCx[k + 1][cen]['center'], LCx[k + 1][cen]['median_width'], LCx[k + 1][cen][
                    'median_height'], 0

            if k <= baseline - 3:
                if LCx[k][cen]['count'] == 0 and LCx[k + 1][cen]['count'] == 0 and LCx[k + 2][cen]['count']== 0:

                    LCx[k][cen]['flag'] = 'inValid'
        k -= 1
    return LCx


import cv2
import numpy as np
def group_points_engine_weaving(collect_det_dots,baseline,lane_centers,roi_up,roi_down,roi_left,roi_right,max_skip_N,w,cnt):
    collect_det_dots__=collect_det_dots

    roi_up_band = int(roi_up+max_skip_N)
    roi_down_band = int(roi_down+max_skip_N)
    dict_save_data_each_y = None

    tem_upperband = baseline - roi_up_band
    tem_downband = baseline + roi_down_band
    ROI_upper = baseline - roi_up_band
    ROI_bottom = baseline + roi_down_band
    near_boundary = False
    if dict_save_data_each_y == None:
        dict_save_data_each_y = {}
        k = baseline - roi_up_band
        while (k < baseline + roi_down_band + 1):
            dict_save_data_each_y[k] = []
            del_item = []
            for vehicle in collect_det_dots__:
                if vehicle[1] == k and vehicle[0] >= roi_left and vehicle[0] <= roi_right:
                    for contour in cnt:
                        in_cnt = cv2.pointPolygonTest(contour, (vehicle[0], vehicle[1]), False)
                        if in_cnt > 0:
                            dict_save_data_each_y[k].append(vehicle)
                            # cv2.circle(frame, (int(vehicle[0]), int(vehicle[1])), 3, (0, 0, 0), 2)
                            if vehicle[0] - roi_left< vehicle[2]/6:
                                if vehicle[1]>=baseline and vehicle[1]<tem_downband:
                                    tem_downband = vehicle[1]
                                    near_boundary = True
                                elif vehicle[1]<baseline and vehicle[1]>tem_upperband:
                                    tem_upperband = vehicle[1]
                                    near_boundary = True
                            elif roi_right - vehicle[0] < vehicle[2]/6:
                                if vehicle[1]>=baseline and vehicle[1]<tem_downband:
                                    tem_downband = vehicle[1]
                                    near_boundary = True
                                elif vehicle[1]<baseline and vehicle[1]>tem_upperband:
                                    tem_upperband = vehicle[1]
                                    near_boundary = True

            k += 1

    if near_boundary:
        ROI_upper = tem_upperband
        ROI_bottom = tem_downband
    valid_flag = 'Valid'
    LCx = {}
    LCx = LCx.fromkeys(range(baseline - roi_up_band, baseline + roi_down_band))
    # print("baseline - roi_up_band",baseline - roi_up_band)
    # print("baseline + roi_down_band",baseline + roi_down_band)
    # print("roi_upper",ROI_upper)
    # print("ROI_bottom",ROI_bottom)
    k = baseline - roi_up_band
    while(k<baseline + roi_down_band+1):
        LCx[k] = {}
        LCx[k].fromkeys(lane_centers)
        for kk in lane_centers:
            LCx[k][kk] = {}
            LCx[k][kk].fromkeys(['datapoints', 'center', 'count', 'median_width', 'median_height', 'flag'])
            if k==baseline:
                LCx[k][kk]['datapoints'], LCx[k][kk]['center'], LCx[k][kk]['count'], LCx[k][kk]['median_width'], \
                LCx[k][kk]['median_height'], LCx[k][kk]['flag'] = [], kk, 1, 0, 0, valid_flag
            else:
                LCx[k][kk]['datapoints'],LCx[k][kk]['center'],LCx[k][kk]['count'], LCx[k][kk]['median_width'],LCx[k][kk]['median_height'],LCx[k][kk]['flag']= [],kk,0,0,0,valid_flag
        k+=1
    k = baseline+1
    while(k<ROI_bottom+1):
      if k in dict_save_data_each_y.keys():
        a = dict_save_data_each_y[k]
        # print(f"Current K:{k}. Current a:{a}")
        if a != []:
            a = sorted(a)
        width = []
        height=[]
        for item in a:
            width.append(item[2])
            height.append(item[3])

        for cen in list(LCx[k].keys()):
          if k-1 in LCx.keys() and cen in list(LCx[k-1].keys()):
            del_=[]
            for j in a:
                if LCx[k-1][cen]['count']!= 0:
                    last_center = LCx[k- 1][cen]['center']
                else:
                    last_center = 0
                    for y in range(k, baseline - 1, -1):
                        if LCx[y][cen]['count']!= 0:
                            last_center = LCx[k-1][cen]['center']
                            break

                if abs(j[0] - last_center) < np.median(width)*1/3:
                    LCx[k][cen]['datapoints'].append(j)
                    del_.append(j)
            for j in del_:
             a.remove(j)
            if LCx[k][cen]['datapoints'] != []:
                point_x = []
                w=[]
                h=[]
                for point in LCx[k][cen]['datapoints']:
                    point_x.append(point[0])
                    w.append(point[2])
                    h.append(point[3])
                LCx[k][cen]['center'] ,LCx[k][cen]['median_width'], LCx[k][cen]['median_height'],LCx[k][cen]['count']= np.mean(point_x), np.median(w),np.median(h),len(LCx[k][cen]['datapoints'])
            else:
                    LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                        'count'] = LCx[k-1][cen]['center'], LCx[k-1][cen]['median_width'], LCx[k-1][cen]['median_height'], 0

            if k >= baseline + 3:
                if LCx[k][cen]['count'] == 0 and LCx[k - 1][cen]['count'] == 0 and LCx[k - 2][cen]['count'] == 0:

                        LCx[k][cen]['flag'] = 'inValid'

      k+=1
    k = baseline - 1
    while (k >= ROI_upper):
        a = dict_save_data_each_y[k]
        if a != []:
            a = sorted(a)
        width = []
        height = []
        for item in a:
            width.append(item[2])
            height.append(item[3])

        for cen in list(LCx[k].keys()):
            del_=[]
            for j in a:
                if LCx[k+1][cen]['count']!= 0:
                    last_center = LCx[k+1][cen]['center']
                else:
                    last_center = 0
                    for y in range(k, baseline+1):
                        if LCx[y][cen]['count']!= 0:
                            last_center = LCx[k+1][cen]['center']
                            break
                if abs(j[0] - last_center) < np.median(width)*1/2:
                    LCx[k][cen]['datapoints'].append(j)
                    del_.append(j)
            for j in del_:
                a.remove(j)
            if LCx[k][cen]['datapoints'] != []:
                point_x = []
                w=[]
                h=[]
                for point in LCx[k][cen]['datapoints']:
                    point_x.append(point[0])
                    w.append(point[2])
                    h.append(point[3])
                LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                    'count'] = np.mean(point_x), np.median(w), np.median(h), len(LCx[k][cen]['datapoints'])

            else:

                LCx[k][cen]['center'], LCx[k][cen]['median_width'], LCx[k][cen]['median_height'], LCx[k][cen][
                    'count'] = LCx[k + 1][cen]['center'], LCx[k + 1][cen]['median_width'], LCx[k + 1][cen][
                    'median_height'], 0

            if k <= baseline - 3:
                if LCx[k][cen]['count'] == 0 and LCx[k + 1][cen]['count'] == 0 and LCx[k + 2][cen]['count']== 0:

                    LCx[k][cen]['flag'] = 'inValid'
        k -= 1

    return LCx