import cv2
import numpy as np
def blob_detection(binary_image):
    # im = cv2.imread(binary_image, cv2.IMREAD_GRAYSCALE)
    # im = cv2.bitwise_not(binary_image)

    # params = cv2.SimpleBlobDetector_Params()
    #
    # blob_detector = cv2.SimpleBlobDetector_create(params)
    # keypoints = blob_detector.detect(binary_image)
    # print("keypoints",keypoints)
    # for keypint in keypoints:
    #     binary_image = cv2.drawKeypoints(binary_image, keypint, np.array([]), (0, 0, 255),
    #                                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    #
    #
    #     print("im_with_keypoints",keypint)
    # cv2.imshow("blob image",binary_image)
    # cv2.waitKey(1000)
    # print("thresh",thresh)
    ret, th1 = cv2.threshold(binary_image, 127, 255, cv2.THRESH_BINARY)
    contours = cv2.findContours(th1, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_NONE)[0]
    threshold_blob_area=2
    print("contours",len(contours))
    colors = [(0,255,0),(255,255,255),(0,0,255),(255,0,255),(255,0,0),(255,255,0)]
    for i in range(1, len(contours)):
        # index_level = int(hierarchy[0][i][1])
        # if index_level<=i:
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            print("area",area)
            if area>threshold_blob_area:
                binary_image = cv2.drawContours(binary_image, [cnt], -1, colors[i], 3)

                ellipse = cv2.fitEllipse(cnt)
                binary_image = cv2.ellipse(binary_image, ellipse, (0, 255, 0), 2)

    cv2.imshow("heatmap",binary_image)
    cv2.waitKey(100000)

