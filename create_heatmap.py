import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cmap
import numpy as np
import seaborn as sns
from sklearn.linear_model import LinearRegression


def create_heatmap(vehicles, im):
    heatmap_centroid = np.zeros_like(im[:,:,0]).astype(np.float)
    heatmap_area = np.zeros_like(im[:, :, 0]).astype(np.float)
    h,w = im.shape[:2]


    for veh in vehicles:
            if veh[-1]>0.35:
                heatmap_centroid[veh[1]][veh[0]] =1
                heatmap_area[int(veh[1]-veh[3]/2):int(veh[1]+veh[3]/2),int(veh[0]-veh[2]/2):int(veh[0]+veh[2]/2)]+=1
    # print(type(heatmap_area))
    # ax = sns.heatmap(heatmap_area, annot=True)
    # sns.heatmap(heatmap_area, annot=True,fmt='f')

    heatmap_area[heatmap_area < 200] = 0
    heatmap_area[heatmap_area >= 200] = 1
    heatmap_centroid[heatmap_centroid < 1] = 0
    plt.imshow(heatmap_area, cmap='hot')
    plt.colorbar()
    plt.savefig("heatmap_area.png")
    plt.show()
    plt.imshow(heatmap_centroid, cmap='hot')
    plt.colorbar()
    plt.savefig("heatmap_centroid.png")
    plt.show()
    # x_ = []
    # heat_x = []
    # y_ = []
    # heat_y = []
    # # print("heatmap",np.sum(heatmap_centroid,axis=0),"len",len(np.sum(heatmap_centroid,axis=0)))
    # plt.plot(np.sum(heatmap_centroid, axis=0))
    # plt.show()
    # plt.plot(np.sum(heatmap_centroid, axis=1))
    # plt.show()
    # plt.plot(np.sum(heatmap_area, axis=0))
    # plt.show()
    # plt.plot(np.sum(heatmap_area, axis=1))
    # plt.show()
    # img_gray = cv2.cvtColor(heatmap_centroid, cv2.COLOR_BGR2GRAY)
    # img_blur = cv2.GaussianBlur(heatmap_centroid, (3, 3), 0)
    # slice1Copy = np.uint8(img_blur)
    # slice1Copy = cv2.Canny(image=slice1Copy, threshold1=100, threshold2=200)  # Canny Edge
    # cv2.imshow("image",slice1Copy)
    # cv2.waitKey(10000)
    print(heatmap_centroid.shape[:2])
    left_most_boundary = []
    right_most_boundary = []
    left_most_boundary_x_list = []
    for i in range(h):

        for j in range(w):
            if j<w-1:
              heatmap_area[i][j]=heatmap_area[i][j+1]-heatmap_area[i][j]
            else:
                heatmap_area[i][j]=0
        if i > h / 2:
         if next((i for i, x in enumerate(list( heatmap_area[i])) if x), None)!=None:
             left_most_boundary.append((i, next((i for i, x in enumerate(list( heatmap_area[i])) if x), None)))
        # if 1 in list(heatmap_centroid[i]):
        #
        #     if i>h/2:
        #          left_most_boundary.append((i, list(heatmap_centroid[i]).index(1)))
        #          left_most_boundary_x_list.append(list(heatmap_centroid[i]).index(1))
        reversed_list = list(heatmap_area[i])[::-1]
        if -1 in reversed_list:
         # first_index_in_reversed = reversed_list.index(-1)
         if next((i for i, x in enumerate(reversed_list) if x), None) != None:
             last_index = len(heatmap_area[i]) - 1 - next((i for i, x in enumerate(reversed_list) if x), None)
             if i>h/2:
               right_most_boundary.append((i, last_index))

        # print(np.diff(heatmap_area[i]))
    for i in range(len(left_most_boundary)):
        cv2.circle(heatmap_area, (left_most_boundary[i][1], left_most_boundary[i][0]), 2, (255, 0, 0), 2)
    for i in range(len(left_most_boundary)):
        cv2.circle(heatmap_area, (right_most_boundary[i][1], right_most_boundary[i][0]), 2, (255, 0, 0), 2)
    # cv2.imshow("img",heatmap_area)
    # cv2.waitKey(10000)
    x=np.array(left_most_boundary)[:,1].reshape((-1, 1))
    y=np.array(left_most_boundary)[:,0]
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x,y)
    print("r_sq",r_sq)
    print('slope:', model.coef_)
    print('intercept:', model.intercept_)
    # print("1d",)
    y_pred = model.predict(x)
    print("x",x)
    print("y",y_pred)
    for i in range(len(left_most_boundary)):

        cv2.circle(heatmap_area,(x[i][0],int(y_pred[i])),2,(255,0,0),2)
    x=np.array(right_most_boundary)[:,1].reshape((-1, 1))
    y=np.array(right_most_boundary)[:,0]
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x,y)
    print("r_sq",r_sq)
    print('slope:', model.coef_)
    print('intercept:', model.intercept_)
    # print("1d",)
    y_pred = model.predict(x)
    print("x",x)
    print("y",y_pred)
    for i in range(len(right_most_boundary)):

        cv2.circle(heatmap_area,(x[i][0],int(y_pred[i])),2,(255,0,0),2)
    # for i in range(len(right_most_boundary)):
    #     cv2.circle(heatmap_centroid, (right_most_boundary[i][1], right_most_boundary[i][0]), 2, (255, 0, 0), 2)
    cv2.imshow("original and fitted boundary",heatmap_area)
    cv2.waitKey(0)
    # print("heatmap center",heatmap_centroid)
    # heatmap_centroid=np.uint8(heatmap_centroid)
    # contours, hierarchy = cv2.findContours(heatmap_centroid,
    #                                        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # print("contours",contours)
    # # cv2.imshow('Canny Edges After Contouring', heatmap_centroid)
    # for contour in contours:
    #  cv2.drawContours(heatmap_centroid, contour, -1, (0, 255, 0), 3)
    #
    # cv2.imshow('Contours', heatmap_centroid)

    cv2.waitKey(0)




    #
    # heatmap_centroid=heatmap_centroid/np.amax(heatmap_centroid)*255
    # heatmap_area=heatmap_area/np.amax(heatmap_area)*255
    # plt.imshow(heatmap_centroid)
    # plt.colorbar()
    # plt.savefig("heatmap_centroid.png")
    # plt.show()
    # plt.imshow(heatmap_area)
    # plt.colorbar()
    # plt.savefig("heatmap_area.png")
    # plt.show()
    # (thresh, binary_heatmap_centroid) = cv2.threshold(np.uint8(heatmap_centroid), 1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # (thresh, binary_heatmap_area) = cv2.threshold(np.uint8(heatmap_area), 1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # gray_heatmap_centroid = cv2.cvtColor(heatmap_centroid, cv2.COLOR_BGR2GRAY)
    # gray_heatmap_area = cv2.cvtColor(heatmap_area, cv2.COLOR_BGR2GRAY)

    # plt.imshow(binary_heatmap_centroid)
    # plt.colorbar()
    # plt.savefig("heatmap_centroid.png")
    # plt.show()
    # plt.imshow(binary_heatmap_area)
    # plt.colorbar()
    # plt.savefig("road.png")
    # plt.show()
    #
    # data = 255 * heatmap_centroid  # Now scale by 255
    # img = data.astype(np.uint8)
    # cv2.imshow("Window", img)
    # cv2.imwrite("uint8_heatmpa_cent.png",img)
    # # cv2.waitKey(100000)
    # heatmap_centroid = cv2.applyColorMap(heatmap_centroid, cv2.COLORMAP_JET)
    # binary_heatmap_centroid = cv2.cvtColor(heatmap_centroid, cv2.COLOR_BGR2GRAY)

    # thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # # gray_heatmap_centroid = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # (thresh, binary_heatmap_centroid) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return np.uint8(heatmap_centroid)
    # cv2.imshow("heatmap_binary",gray_heatmap_centroid)
    # cv2.waitKey(10000000)
