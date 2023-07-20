def lane_boundaries_engine(lane_center_table,lane_centers,median_width_height_each_y,w):
    """
      Function:  lane_boundaries_engine
      --------------------
      generate lane boundary of each lane based on the lane curve
      and estimated lane width at current y pixel position;

        lane_center_table: lane center position in all y pixel position in the ROI;
        generated in file Create_Lane_Center_Table.py
        lane_centers: lane center position in current ROI
        median_width_height_each_y: estimated car's median width and height in current ROI

       returns: lane_boundaries, containing each lane's left and right lane boundary
                position along the lane curves in the ROI
    """
    global lane_annotation_right_boundary, lane_annotation_left_boundary, index
    lane_annotation_right_boundary = 0
    lane_annotation_left_boundary = 0
    lane_boundaries = {}
    small_margin = 10
    large_margin = 65
    if len(lane_centers)>0:
        y_list=list(median_width_height_each_y[lane_centers[0]].keys())
        lane_boundaries.fromkeys(lane_centers)
        for lane in lane_centers:
            lane_boundaries[lane]={}
            lane_boundaries[lane].fromkeys(y_list)

        for lane in lane_centers:
         for y in y_list:
                lane_boundaries[lane][y]={}
                lane_boundaries[lane][y].fromkeys(['center','left_boundary_x','right_boundary_x'])
                lane_boundaries[lane][y]['center']=0
                lane_boundaries[lane][y]['left_boundary_x']=0
                lane_boundaries[lane][y]['right_boundary_x']=0


        y_mid = y_list[int(len(y_list)/2)]
        if len(lane_centers)<=1:
         index=0
         for lane in lane_centers:
            for y in y_list:
                if lane_center_table[y][lane_centers.index(lane)] - \
                                                median_width_height_each_y[lane][y_mid][0][0]*1.5>=0:
                    lane_annotation_left_boundary = lane_center_table[y][lane_centers.index(lane)] - \
                                                    median_width_height_each_y[lane][y_mid][0][0]*1.5
                else:
                    lane_annotation_left_boundary=0
                if lane_center_table[y][index] + median_width_height_each_y[lane][y_mid][0][0]*1.5<=w:
                    lane_annotation_right_boundary = lane_center_table[y][index] + median_width_height_each_y[lane][y_mid][0][0]*1.5
                else:
                    lane_annotation_right_boundary = w
                lane_boundaries[lane_centers[index]][y]['center'] = lane_center_table[y][
                    index]
                # if abs(lane_annotation_left_boundary - lane_center_table[y][index]) <= 10:
                #     lane_annotation_left_boundary = lane_center_table[y][index] - 65
                # if abs(lane_annotation_right_boundary - lane_center_table[y][index]) <= 10:
                #     lane_annotation_right_boundary = lane_center_table[y][index] + 65
                lane_boundaries[lane_centers[index]][y][
                    'left_boundary_x'] = lane_annotation_left_boundary
                lane_boundaries[lane_centers[index]][y][
                    'right_boundary_x'] = lane_annotation_right_boundary
            index+=1
        else:
             index =0
             for lane in lane_centers:
                 for y in y_list:
                     if index==0:

                         if lane_center_table[y][lane_centers.index(lane)] - \
                                 median_width_height_each_y[lane][y_mid][0][0] * 1.5 >= 0:
                             lane_annotation_left_boundary = lane_center_table[y][lane_centers.index(lane)] - \
                                                             median_width_height_each_y[lane][y_mid][0][0] * 1.5
                         else:
                             lane_annotation_left_boundary = 0
                         lane_annotation_right_boundary = (lane_center_table[y][index + 1] +
                                                           lane_center_table[y][index]) / 2

                     elif index==len(lane_centers)-1:
                             lane_annotation_left_boundary = (lane_center_table[y][index] +
                                                          lane_center_table[y][index - 1]) / 2
                             if lane_center_table[y][index] + median_width_height_each_y[lane][y_mid][0][0]*1.5<=w:
                                lane_annotation_right_boundary = lane_center_table[y][index] + median_width_height_each_y[lane][y_mid][0][0]*1.5
                             else:
                                lane_annotation_right_boundary = w
                     else:

                             lane_annotation_left_boundary = (lane_center_table[y][index] +
                                                          lane_center_table[y][index - 1]) / 2
                             lane_annotation_right_boundary = (lane_center_table[y][index + 1] +
                                                               lane_center_table[y][index]) / 2

                     lane_boundaries[lane_centers[index]][y]['center'] = lane_center_table[y][
                         index]
                     # if abs(lane_annotation_left_boundary-lane_center_table[y][index])<=small_margin:
                     #     lane_annotation_left_boundary = lane_center_table[y][index]-large_margin
                     # if abs(lane_annotation_right_boundary - lane_center_table[y][index]) <= small_margin:
                     #     lane_annotation_right_boundary = lane_center_table[y][index] + large_margin
                     lane_boundaries[lane_centers[index]][y][
                         'left_boundary_x'] = lane_annotation_left_boundary
                     lane_boundaries[lane_centers[index]][y][
                         'right_boundary_x'] = lane_annotation_right_boundary
                 index+=1
    return lane_boundaries