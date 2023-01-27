import numpy as np
def lane_center_table_engine(h,road_fitting_equations):
    """
      Function:  lane_center_table_engine
      --------------------
      generate a lane center table of all the y pixel position inside the ROI

        h: height of the ROI
        road_fitting_equations: fitted curve equations

       returns: lane_center_table which contains lane center position in all y pixel position in the ROI
    """
    lane_center_table={}
    lane_center_table=lane_center_table.fromkeys(range(h))
    for key in range(h):
        lane_center_table[key]=[]
        for lane in list(road_fitting_equations.keys()):

            poly1d_fn = np.poly1d(road_fitting_equations[lane][0])
            pts_x = poly1d_fn(key)
            lane_center_table[key].append(pts_x)
    return  lane_center_table