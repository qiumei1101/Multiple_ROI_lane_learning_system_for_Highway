"""
This module calculates lanes in a given video stream

Current Author      :   Anup Mulay (+1-317-998-0306 | anup.mulay96@gmail.com | anmulay@iupui.edu)
Last Edited Date    :   March 1, 2021
"""

from statistics import median_low

import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as plot
from scipy.signal import find_peaks
import os
# import FileSystem
"""
Mean Filter Logic
It uses the sliding window to smooth the generated peaks
"""


def mean_filter_d(samples, window_size=5):
    if not window_size & 1:
        assert ValueError
    samples = np.pad(samples, window_size, mode='constant')
    output = [0] * len(samples)
    i = 0
    length = len(samples)
    mid_offset = window_size >> 1
    while i <= length - window_size:
        output[i + mid_offset] = sum(samples[i: i + window_size]) / window_size
        i += 1
    return output[window_size:-window_size]


"""
next_peak : The next detected probable peak from histogram to be a lane center or not 
next_peak should not be within 1.2*med_width x-axis distance to any detected lanes
"""


def checkLaneWithDifference_1point2(next_peak, X_final, med_width):
    print("checkLaneWithDifference_1point2")
    isNextPeakIsALane = True
    for i in range(len(X_final)):
        val = next_peak - X_final[i]
        if abs(val) < 1.2 * med_width:
            isNextPeakIsALane = False
            break
    if isNextPeakIsALane == True:
        return True
    else:
        return False


"""
next_peak should not be less than 0.70*med_width x-axis distance to any detected lanes
"""


def checkLaneWithDifference_0point70(next_peak, X_final, med_width, X_original, heights_original):
    print("checkLaneWithDifference_0point70")
    isNextPeakIsALane = True
    for i in range(len(X_final)):
        val = next_peak - X_final[i]
        if abs(val) < 0.7 * med_width:
            isNextPeakIsALane = False
            break
    if isNextPeakIsALane == True:
        return True
    else:
        return False

def checkLaneWithDifference_0point50_height(next_peak, X_final, med_width, X_original, heights_original):
    print("checkLaneWithDifference_0point50_height")
    isNextPeakIsALane = True
    for i in range(len(X_final)):
        val = next_peak - X_final[i]
        index = X_original.index(next_peak)
        index_current = X_original.index(X_final[i])
        # print("here111", heights_original[index])
        height_diff = abs(heights_original[index] - heights_original[index_current])
        # print(height_diff)
        # print(heights_original[index_current] * .35)
        # print(height_diff < (heights_original[index_current] * .35))
        # print(abs(val) > .5 * med_width)
        if abs(val) > .5 * med_width and height_diff < (heights_original[index_current] * .35):
            print("is a lane")
            isNextPeakIsALane = True
            break
        else:
            isNextPeakIsALane = False
            break
    if isNextPeakIsALane == True:
        return True
    else:
        return False


"""
Height of the next_peak should be less than 0.15 of closet lane or adjacent lanes 
"""


def checkPeakLessThan_0point5(next_peak, X_final, med_width, X_original, heights_original):
    diff1 = -1
    diff2 = -1

    print("checkPeakLessThan_0point5")

    # Traverse detected lane centers
    for i in range(len(X_final)):
        if X_final[i] < next_peak:  # detected lane centers smaller than next_peak
            if X_final[i] == X_final[-1]:  # all detected lane centers smaller than next_peak
                left_adj_lane = X_final[-1]  # Last element of X_final is left adjacent lane
                # print("Left Adjacent Lane ", left_adj_lane)
                diff1 = abs(next_peak - left_adj_lane)
                # print("Difference betweeen Next_Peak and Left Adjacent Lane ", diff1)
                break
            else:
                continue
        else:
            if i == 0:
                diff1 = 0
                break
            else:
                left_adj_lane = X_final[i - 1]  # next_peak is between 2 detected lane centers
                # print("Left Adjacent Lane ", left_adj_lane)
                diff1 = abs(next_peak - left_adj_lane)
                # print("Difference betweeen Next_Peak and Left Adjacent Lane ", diff1)
                break

    # Traverse detected lane centers
    for i in range(len(X_final)):
        # print(i)
        if X_final[len(X_final) - i - 1] > next_peak:  # detected lane centers greater than next_peak
            if X_final[len(X_final) - i - 1] == X_final[0]:  # all detected lane centers greater than next_peak
                right_adj_lane = X_final[0]  # First element of X_final is right adjacent lane
                # print("Right Adjacent Lane ", right_adj_lane)
                diff2 = abs(next_peak - right_adj_lane)
                # print("Difference between Next_Peak and Right Adjancent Lane", diff2)
                break
            else:
                continue
        else:
            if X_final[len(X_final) - i - 1] == X_final[len(X_final) - 1]:
                diff2 = 0
                break
            else:
                right_adj_lane = X_final[len(X_final) - i]  # next_peak is between 2 detected lane centers
                # print("Right Adjacent Lane ", right_adj_lane)
                diff2 = abs(next_peak - right_adj_lane)
                # print("Difference between Next_Peak and Right Adjancent Lane", diff2)
                break

    if diff1 == 0:  # if there is no left adjacent lane detected
        if diff2 >= 0.7 * med_width and diff2 <= 1.2 * med_width:  # Diff(right adj lane) in the range 0.7*median_width to 1.2*median
            closet_lane = right_adj_lane  # then filter on the height of right adj lane
            indx = X_original.index(next_peak)
            next_peak_height = heights_original[indx]
            # print("Height of Next_Peak ", next_peak_height)

            indx_closet_lane = X_original.index(closet_lane)
            closet_lane_height = heights_original[indx_closet_lane]
            # print("Height Of Right Adjacent Lane Height ", closet_lane_height)

            if next_peak_height < 0.15 * closet_lane_height:  # height(next_peak) less than 0.15 * height(closet lane)
                print("Height Of Next_Peak is Less than 0.5 * right_adj_lane_height")
                return True
            else:
                return False
        else:
            return False

    elif diff2 == 0:  # if there is no right adjacent lane detected
        if (
                diff1 >= 0.7 * med_width and diff1 <= 1.2 * med_width):  # Diff(left adj lane) in the range 0.7*median_width to 1.2*median
            closet_lane = left_adj_lane  # then filter on the height of left adj lane
            indx = X_original.index(next_peak)
            next_peak_height = heights_original[indx]
            # print("Height of Next_Peak ", next_peak_height)

            indx_closet_lane = X_original.index(closet_lane)
            closet_lane_height = heights_original[indx_closet_lane]
            # print("Height Of Right Adjacent Lane Height ", closet_lane_height)

            if next_peak_height < 0.15 * closet_lane_height:  # height(next_peak) less than 0.15 * height(closet lane)
                print("Height Of Next_Peak is Less than 0.5 * left_adj_lane_height")
                return True
            else:
                return False
        else:
            return False

    # Here for the next_peak we have both left adj lane and right adj lane
    elif (diff1 >= 0.7 * med_width and diff1 <= 1.25 * med_width) and (
            diff2 >= 0.7 * med_width and diff2 <= 1.25 * med_width):
        print("Diff1 and Diff2 are within the Range >=0.7 and <= 1.2")
        indx = X_original.index(next_peak)
        next_peak_height = heights_original[indx]
        # print("Height of Next_Peak ", next_peak_height)

        indx_left_adj_lane = X_original.index(left_adj_lane)
        left_adj_lane_height = heights_original[indx_left_adj_lane]
        # print("Height Of Left Adjacent Lane Height ", left_adj_lane_height)

        indx_right_adj_lane = X_original.index(right_adj_lane)
        right_adj_lane_height = heights_original[indx_right_adj_lane]
        # print("Height Of Right Adjacent Lane Height", right_adj_lane_height)

        # height(next_peak) is less than either left or right adj lane
        if next_peak_height < 0.15 * left_adj_lane_height or next_peak_height < 0.15 * right_adj_lane_height:
            print("Height Of Next_Peak is Less than 0.5 * left_adj_lane_height or right_adj_lane_height")
            return True
        else:
            print("Height Of Next_Peak is NOT Less than 0.5 * left_adj_lane_height OR right_adj_lane_height")
            return False
    else:
        print("Either Diff1 or Diff2 are NOT within the Range >=0.7 and <= 1.2")
        return False


def checkHeightDiffBetweenPeakANDValley(next_peak, X_final, X_original, heights_original, valley_x, Local_Minima):
    diff1 = -1
    diff2 = -1

    print("checkHeightDiffBetweenPeakANDValley")

    indx = X_original.index(next_peak)
    next_peak_height = heights_original[indx]
    # print("Next_Peak Height", next_peak_height)

    # Traverse detected lane centers
    for i in range(len(X_final)):
        if X_final[i] < next_peak:  # detected lane centers smaller than next_peak
            if X_final[i] == X_final[-1]:  # all detected lane centers smaller than next_peak
                left_adj_lane = X_final[-1]  # Last element of X_final is left adjacent lane
                # print("Left Adjacent Lane ", left_adj_lane)
                diff1 = abs(next_peak - left_adj_lane)
                # print("Difference betweeen Next_Peak and Left Adjacent Lane ", diff1)
                break
            else:
                continue
        else:
            if i == 0:
                diff1 = 0
                break
            else:
                left_adj_lane = X_final[i - 1]  # next_peak is between 2 detected lane centers
                # print("Left Adjacent Lane ", left_adj_lane)
                diff1 = abs(next_peak - left_adj_lane)
                # print("Difference betweeen Next_Peak and Left Adjacent Lane ", diff1)
                break

    # Traverse detected lane centers
    for i in range(len(X_final)):
        # print(i)
        if X_final[len(X_final) - i - 1] > next_peak:  # detected lane centers greater than next_peak
            if X_final[len(X_final) - i - 1] == X_final[0]:  # all detected lane centers greater than next_peak
                right_adj_lane = X_final[0]  # First element of X_final is right adjacent lane
                # print("Right Adjacent Lane ", right_adj_lane)
                diff2 = abs(next_peak - right_adj_lane)
                # print("Difference between Next_Peak and Right Adjancent Lane", diff2)
                break
            else:
                continue
        else:
            if X_final[len(X_final) - i - 1] == X_final[len(X_final) - 1]:
                diff2 = 0
                break
            else:
                right_adj_lane = X_final[len(X_final) - i]  # next_peak is between 2 detected lane centers
                print("Right Adjacent Lane ", right_adj_lane)
                diff2 = abs(next_peak - right_adj_lane)
                print("Difference between Next_Peak and Right Adjancent Lane", diff2)
                break

    if diff1 == 0:
        closest_lane = right_adj_lane
    elif diff2 == 0:
        closest_lane = left_adj_lane
    elif (diff1 != 0) and (diff2 != 0) and (diff1 < diff2):
        closest_lane = left_adj_lane
    else:
        closest_lane = right_adj_lane

    ''' Find Valley between next_peak and closet lane '''

    # print("Closet lane", closest_lane)
    diffBtwPeakAndAdjValley = 0
    valley_height_req = -1
    # print("X values of Valleys ", valley_x)
    # print("Y : Heights Of Valleys", Local_Minima)

    for i in range(len(valley_x)):
        if (closest_lane < valley_x[i] < next_peak) or (next_peak < valley_x[i] < closest_lane):
            print(closest_lane, " < ", valley_x[i], " < ", next_peak, " OR ", next_peak, " < ", valley_x[i], " < ",
                  closest_lane)
            valley_req = valley_x[i]
            # print("Required Valley ", valley_req)
            indx_valley_x = valley_x.index(valley_req)
            valley_height_req = Local_Minima[indx_valley_x]
            # print("Req valley Height", valley_height_req)
            diffBtwPeakAndAdjValley = abs(valley_height_req - next_peak_height)
            # print("Difference Between Next_Peak_Height and Valley Height ", diffBtwPeakAndAdjValley)
            break

    # Filtering on height(next_peak) and height(adjacent valley)
    if valley_height_req != -1 and valley_height_req < 0.02:
        if ((diffBtwPeakAndAdjValley / next_peak_height) > 0.97):
            return True
        else:
            return False
    elif (diffBtwPeakAndAdjValley != 0) and (diffBtwPeakAndAdjValley < 0.35 * next_peak_height):
        # print(0.35 * next_peak_height)
        # print(diffBtwPeakAndAdjValley < 0.35 * next_peak_height)
        print("Difference Of Next_Peak_height and Valley Height is Less than next_peak_height")
        return False
    else:
        print("Difference Of Next_Peak_height and Valley Height is NOT Less than next_peak_height")
        return True


"""
Start of Lane Finding Module

This module generated the lane center points for the give road Scenario
-----------------------------------------------------------------------------

Input : 
        collect_det_dots : Vehicles detection: 10,000 Vehicles' information
        baseline: Here the baseline need to be modified because the vehicle detection results are with respect to ROI

Output :
        required_cars : 10,000 vehicles information : Can be removed (Redundant Output)
        X_final: Final x-axis coordinates of lane centers 

Example: Steps to follow the Algorithm:
        1) From the input collect_det_dots filter the information of cars in 5 Pixel Up and 5 Pixel down the baseline
        2) Populate the information of intersection points and widths of vehicles
        3) Compute the Median width
        4) Generate the Histogram and apply smoothing filter (Iteratively)
        5) Get the information of peaks and valleys
        6) Apply the lane filtering algorithm on each detected probable peak (next_peak)
        7) Return the lane center coordinates  
"""


def lane_finding_engine(frame,learing_cycle,collect_det_dots,remain_cnts, baseline, lane_centers_final,filepath):

    for baseline_ in baseline:
        fig1, ax1 = plot.subplots()
        plt.rcParams['font.size'] = '12'
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"

        # Set tick font size
        for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
            label.set_fontsize(15)
        required_cars = []  # Cars within 10 pixels up and 10 pixels down the baseline
        intersection_points = []  # x-axis coordinates of cars within 10 pixels up and 10 pixels down the baseline
        widths = []  # bounding box width of cars within 10 pixels up and 10 pixels down the baseline

        for item in collect_det_dots:
            if remain_cnts!=None:
              if cv2.pointPolygonTest(remain_cnts[baseline.index(baseline_)],(item[0],item[1]),False)>0:

                if baseline_[2] - 18< item[1] < baseline_[2] +18 and item[0]>=baseline_[0] and item[0]<=baseline_[1]:

                    required_cars.append(item)

        for item in required_cars:
            intersection_points.append(item[0])

        # Gennerate Histogram

        ##### test
        # 1 [baseline -10, baseline +10]
        if len(intersection_points)==0:
            return []
        elif len(intersection_points)==1:
            lane_centers_final.append((int(intersection_points[0]), baseline_[2],baseline.index(baseline_)))
        else:
            bins_= int(max(intersection_points) - min(intersection_points))
            if bins_<=0:
                bins_=1
            y, x = np.histogram(intersection_points, bins=bins_)
            for i in range(len(y)):
                y[i] = y[i] * 5
            x, y = x[1:-1], y[1:]

            # Apply smooth filter and plot the steps
            ax1.plot(x, y, 'b')


            # Store intersection point and widths
            for item in required_cars:
                intersection_points.append(item[0])
                widths.append(item[2])

            # print("Widths", widths)

            # Compute Median Width
            median_width = median_low(widths)


            filter_len = int(median_width) >> 2
            y = mean_filter_d(y, filter_len)

            ax1.plot(x, y)
            # plot.show()

            y = mean_filter_d(y, filter_len)

            ax1.plot(x, y)
            # plot.show()
            y = mean_filter_d(y, filter_len)

            ax1.plot(x, y)
            # plot.show()

            y = mean_filter_d(y, filter_len)

            ax1.plot(x, y)
            # plot.show();

            y = mean_filter_d(y, filter_len)

            ax1.plot(x, y, 'g')
            # plot.show();

            Y = y
            X = x

            # print("Y values", y)
            # print()

            # Generate Peaks
            peaks, k = find_peaks(y, height=0.032)
            x = np.array(x)[peaks.astype(int)]

            # print("Printing Peaks X")
            for i in x:
                print(i)

            # max_x = max(x)
            # print("Max X", max_x)
            #
            # print("Peak Dictionary", k)

            # X values to X_original
            X_original = list(x)
            heights_original = list(k['peak_heights'])

            Local_Minimas = []
            valleys_x = []

            for i in range(1, len(X) - 1):
                if Y[i] < Y[i - 1] and Y[i] < Y[i + 1]:
                    Local_Minimas.append(Y[i])
                    valleys_x.append(X[i])

            X_final = []
            X_updated = X_original[:]
            heights_updated = heights_original[:]
            if heights_updated!=[]:
                index_max = np.argmax(heights_updated)
                first_lane = X_updated[index_max]

                indx_first_lane = X_updated.index(first_lane)
                X_updated.remove(first_lane)
                heights_updated.remove(heights_updated[indx_first_lane])
                X_final.append(first_lane)

            median_width = 1.255 * median_width

            for i in range(len(X_original) - 1):

                index_max = np.argmax(heights_updated)
                next_peak = X_updated[index_max]

                if checkLaneWithDifference_1point2(next_peak, X_final, median_width) == True:
                    X_final.append(next_peak)

                elif checkLaneWithDifference_0point70(next_peak, X_final, median_width, X_original, heights_original) == False:
                    # print("Distance between peak and adjacent lane is < 0.7*median_width :", next_peak,)

                    if checkLaneWithDifference_0point50_height(next_peak, X_final, median_width, X_original, heights_original):
                        X_final.append(next_peak)
                        # print("Distance between peak and adjacent lane is > 0.5*median_width < .70*median_width and height is close: It is a Lane")

                else:
                    if checkPeakLessThan_0point5(next_peak, X_final, median_width, X_original, heights_original) == True:
                        print("Height Of peak ", next_peak,
                              "is less than 0.5 of the car count in the adjacent lower count lane and this lane is between 0.7D and 1.2D : Its Not a Lane")

                    elif checkHeightDiffBetweenPeakANDValley(next_peak, X_final, X_original, heights_original, valleys_x,
                                                             Local_Minimas) == False:
                        print(
                            "The difference between the height this peak and the valley between this peak and closest lane is small less than the peak height : Its Not a Lane")

                    else:
                        # print("Adding", next_peak, "As a Lane")
                        X_final.append(next_peak)

                X_final.sort()
                # print("Lanes", X_final)

                indx_next_peak = X_updated.index(next_peak)
                X_updated.remove(next_peak)
                heights_updated.remove(heights_updated[indx_next_peak])

                # print("---------------------------------------")

            # print("##############################################")
            del_lanes=[]
            if len(X_final)>2:
                index__=0
                for i in np.diff(X_final):
                    if i<np.max(np.diff(X_final))*0.3:
                        del_lanes.append(X_final[index__+1])
                    index__+=1
            for lene_ in del_lanes:
                X_final.remove(lene_)
            X_final = [int(i) for i in X_final]

            for i in X_final:
                lane_centers_final.append((i,baseline_[2],baseline.index(baseline_)))
                plot.axvline(i, c='r')
                cv2.circle(frame, (int(i), int(baseline_[2])), 6, (0, 0, 255), 7)

            # save_directory = FileSystem.getDirectoryPath("040_lane_center_finding")
            plt.xlabel("Pixel Position at X axis")
            plt.ylabel("Vehicle Number")
            # plt.title("Lane Finding in the ROI")
            filename = str(learing_cycle)+'_'+str(baseline.index(baseline_))+'_'+ "lane.png"
            plot.savefig(os.path.join(filepath,filename))
            plot.close()
            # plot.show()
            print("Final Set of Lanes", X_final)

    return lane_centers_final



