import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
kernel = np.ones((3,3),np.uint8)

def create_heatmap(learning_cycle,vehicles, im,filepath):
    heatmap_area = np.zeros_like(im[:, :, 0]).astype(np.float)
    h, w = im.shape[:2]
    conf=[]
    length_=len(vehicles)
    index =0
    while(index<length_):
        conf.append(vehicles[index][-1])
        index+=1
    a = np.array(conf)
    if len(a)!=0:
        p1 = np.percentile(a, 25)
    else:
        p1 = 0.25

    raito=4.5
    index = 0
    remain_vehicles=[]
    while(index < length_):
            if vehicles[index][-1] >p1:
                remain_vehicles.append(vehicles[index])
                heatmap_area[int(vehicles[index][1]-vehicles[index][3]/raito):int(vehicles[index][1]+vehicles[index][3]/raito),int(vehicles[index][0]-vehicles[index][2]/raito):int(vehicles[index][0]+vehicles[index][2]/raito)]=1
            index+=1

    conf = []
    h_index=[]

    conf_y = {}
    conf_y = conf_y.fromkeys(range(h),[])
    conf_list=[]
    for i in range(h):
        conf_y[i]=[]
    for veh in vehicles:
            conf.append(veh[-1])
            h_index.append(veh[1])
            # if veh[1]==i:
            conf_y[veh[1]].append(veh[-1])
    # fig = plt.figure()
    # plt.rcParams['font.size'] = '12'
    # plt.rcParams["font.weight"] = "bold"
    # plt.rcParams["axes.labelweight"] = "bold"
    # axes = plt.gca()
    # Set tick font size
    # for label in (axes.get_xticklabels() + axes.get_yticklabels()):
    #     label.set_fontsize(12)
    # # plt.hist(conf)
    # #
    # y_range=axes.get_ylim()
    # plt.vlines(p1,y_range[0],y_range[1],colors='k')
    # plt.text(p1,1/2*(y_range[1]-y_range[0]),'25th\n Percentile')
    # # plt.vlines(p2,y_range[0], y_range[1], colors='b')
    # # plt.text(p2, 1 / 2 * (y_range[1] - y_range[0]+50), '95th\n Percent')
    # # plt.vlines(np.mean(conf), y_range[0], y_range[1], colors='r')
    # # plt.text(np.mean(conf), 1 / 2 * (y_range[1] - y_range[0]), 'mean value')
    # plt.show()
    # plt.xlabel("Detection Confidence Score in the whole Frame")
    # plt.ylabel("Vehicle Number")
    # plt.title("Confidence Score Distribution")
    # filename = 'confidence_score.png'
    # plt.savefig(os.path.join(filepath,filename))
    # plt.close()
    h_index_=[]
    for i in range(h):
        if len(conf_y[i])!=0:
            h_index_.append(i)
        #     conf_list.append(0)
        # else:
            conf_list.append(np.mean(conf_y[i]))
    ##### Draw
    # fig, ax = plt.subplots(1)
    # plt.rcParams['font.size'] = '15'
    #
    # # Set tick font size
    # for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    #     label.set_fontsize(15)

    # plt.imshow(heatmap_area, cmap='hot')
    # plt.xlabel("Pixel Position at X axis", fontsize=15)
    # plt.ylabel("Pixel Position at Y axis", fontsize=15)
    # plt.title("Vehicles' Number at each Pixel", fontweight='bold')
    # plt.colorbar()
    # plt.savefig(os.path.join(filepath,"heatmap_area.png"))
    #
    # plt.plot(h_index,conf,'r+')
    # plt.plot(h_index_,conf_list,'.b-')
    # plt.xlabel("Pixel Position at Y axis")
    # plt.ylabel("Detection Confidence Score")
    # # plt.title("Confidence Score at Each Y pixel",fontweight='bold')
    # plt.legend(['Individual Confidence Score', 'Average Confidence Score'])
    # plt.savefig(os.path.join(filepath, "conf.png"))
    # plt.close()
    # plt.show()
    # # plt.show()
    # plt.imshow(heatmap_centroid, cmap='hot')
    # plt.colorbar()
    # plt.savefig(os.path.join(filepath,"heatmap_centroid.png"))
    # plt.show()

    ##################################################find contours

    heatmap_area=heatmap_area*255
    heatmap_area = heatmap_area.astype(np.uint8)

    cv2.imwrite(os.path.join(filepath,str(learning_cycle)+'_'+'binary_heatmap_area_cars.png'), heatmap_area)
    #
    j=0
    i=0
    while(i<h):
        while(j<w):
            num = 0
            num_ = 0
            if i - 1 >= 0 and j - 1 >= 0 and i + 1 <= h - 1 and j + 1 <= w - 1:
                if heatmap_area[i - 1][j] == 255:
                    num += 1
                if heatmap_area[i + 1][j] == 255:
                    num += 1
                if heatmap_area[i][j - 1] == 255:
                    num += 1
                if heatmap_area[i][j + 1] == 255:
                    num += 1
                if heatmap_area[i - 1][j - 1] == 255:
                    num += 1
                if heatmap_area[i + 1][j - 1] == 255:
                    num += 1
                if heatmap_area[i - 1][j - 1] == 255:
                    num += 1
                if heatmap_area[i + 1][j + 1] == 255:
                    num += 1

                if num / 8 >= 1 / 3:
                    heatmap_area[i][j] = 255
            i+=1
            j+=1

    cv2.imwrite(os.path.join(filepath, str(learning_cycle)+'_'+'binary_heatmap_area.png'), heatmap_area)
    return heatmap_area,remain_vehicles

