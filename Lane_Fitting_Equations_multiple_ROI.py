import cv2
import numpy as np


def lane_fitting_engine(LCx,lane_centers,baseline,roi_up,roi_down,h):
    dots_for_alllanes = {}
    dots_for_alllanes.fromkeys(lane_centers)
    dots_for_alllanes_cen = {}
    dots_for_alllanes_cen.fromkeys(lane_centers)
    median_width_height_each_y={}
    median_width_height_each_y.fromkeys(lane_centers)

    key_list=list(range(baseline-roi_up,baseline+roi_down))
    for keyy in lane_centers:
        dots_for_alllanes[keyy] = []
        dots_for_alllanes_cen[keyy] = []
        median_width_height_each_y[keyy]={}

        for key in key_list:
          if key<h:
            median_width_height_each_y[keyy][key]=[]

            if LCx[key][keyy]['flag'] == 'Valid':
                dots_for_alllanes_cen[keyy].append((LCx[key][keyy]['center'], key))

            if LCx[key][keyy]['flag'] == 'Valid':
                if list(LCx.keys())[-1]-key>1:
                  median_width_height_each_y[keyy][key].append((LCx[key][keyy]['median_width'],LCx[key][keyy]['median_height']))
                for item in LCx[key][keyy]['datapoints']:
                    dots_for_alllanes[keyy].append(item)


    colors = [(255, 0, 0), (0, 255, 255), (0, 0, 255), (0, 128, 255), (0, 255, 0), (0, 0, 0), (0, 128, 0), (200, 100, 0),(100,100,100),(120,120,120),(130,120,129),(230,222,120)]

    #check the width and height in each y:
    for lane in lane_centers:
        average_median_width=[]
        average_median_height=[]
        for y in median_width_height_each_y[lane].keys():
               if median_width_height_each_y[lane][y]!=[]:
                       average_median_width.append(median_width_height_each_y[lane][y][0][0])
                       average_median_height.append(median_width_height_each_y[lane][y][0][1])

        for y in median_width_height_each_y[lane].keys():
            if median_width_height_each_y[lane][y]!= []:
              if median_width_height_each_y[lane][y][0][0]==0 or median_width_height_each_y[lane][y][0][1]==0:
                median_width_height_each_y[lane][y]=[]
                median_width_height_each_y[lane][y].append((np.mean(average_median_width), np.mean(average_median_height)))
            else:
                median_width_height_each_y[lane][y].append((np.mean(average_median_width), np.mean(average_median_height)))
    road_fitting_equations={}
    road_fitting_equations.fromkeys(lane_centers,[])
    for key in list(dots_for_alllanes.keys()):
        road_fitting_equations[key]=[]
        px = []
        py = []
        for item in dots_for_alllanes[key]:
            px.append(item[0])
            py.append(item[1])


        #### road fitting
        if px==[] or py == []:
            road_fitting_equations[key].append([])
            continue
        coef = np.polyfit(py, px, 2)

        road_fitting_equations[key].append(coef)
    # print("median_width_height_each_y",median_width_height_each_y)
    return road_fitting_equations,dots_for_alllanes,median_width_height_each_y
