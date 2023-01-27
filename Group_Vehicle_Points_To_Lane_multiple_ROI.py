def group_points_engine(collect_det_dots,baseline,road_bound,lane_centers,roi_up,roi_down,roi_left,roi_right,max_skip_N,w):
    collect_det_dots__=collect_det_dots
    # print("len(", len(collect_det_dots__))
    import numpy as np
    del_lane =[]
    for lane in lane_centers:
        if np.abs(lane-w) <=25 or np.abs(lane-0)<=25:
            del_lane.append(lane)
    for lane in del_lane:
        lane_centers.remove(lane)
    roi_up_band = int(roi_up+max_skip_N)
    roi_down_band = int(roi_down+max_skip_N)
    dict_save_data_each_y = None
    del_dots = []
    dot_width = []
    # for kk in range(len(collect_det_dots__)):
    #     if collect_det_dots__[kk][2] != []:
    #         dot_width.append(int(collect_det_dots__[kk][2]))
    # median_width = np.median(dot_width)
    # for kk in range(len(collect_det_dots__)):
    #     if collect_det_dots__[kk][2]>4*median_width:
    #         del_dots.append(collect_det_dots__[kk])
    # for item in del_dots:
    #     collect_det_dots__.remove(item)
    if dict_save_data_each_y == None:
        dict_save_data_each_y = {}
        k = baseline - roi_up_band
        while(k<baseline+roi_down_band+1):
            dict_save_data_each_y[k] = []
            del_item = []
            dict_save_data_each_y[k] = [item for item in collect_det_dots__ if item[1] == k and item[0]>=roi_left and item[0]<=roi_right]

            k+=1

        # for k in range(baseline - roi_up_band, baseline + roi_down_band+1):
        #
        #     for item in collect_det_dots__:
        #         if item[1] == k and item[0]>lef_bound and item[0]<right_bound:
        #             dict_save_data_each_y[k].append(item)
        #             del_item.append(item)
        #

    valid_flag = 'Valid'
    LCx = {}
    LCx = LCx.fromkeys(range(baseline - roi_up_band, baseline + roi_down_band+1))
    k = baseline - roi_up_band
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
        # for j in a:
        #     if j[2]>1.5*np.median(width) or j[3]>1.5*np.median(height):
        #         a.remove(j)
        for cen in list(LCx[k].keys()):
          if k-1 in LCx.keys() and cen in list(LCx[k-1].keys()):
            del_=[]
            for j in a:
                if abs(j[0] - LCx[k-1][cen]['center']) < np.median(width)*1/3:
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
    while (k >= baseline - roi_up_band):
        a = dict_save_data_each_y[k]
        if a != []:
            a = sorted(a)
        width = []
        height = []
        for item in a:
            width.append(item[2])
            height.append(item[3])
        # for j in a:
        #     if j[2] > 2 * np.median(width) or j[3] > 2 * np.median(height):
        #         a.remove(j)
        for cen in list(LCx[k].keys()):
            del_=[]
            for j in a:
                if abs(j[0] - LCx[k + 1][cen]['center']) < np.median(width)*1/4:
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

