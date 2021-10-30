im = cv2.imread(im, cv2.IMREAD_GRAYSCALE)
im = cv2.bitwise_not(im)

params = cv2.SimpleBlobDetector_Params()

blob_detector = cv2.SimpleBlobDetector_create(params)
keypoints = blob_detector.detect(im)
keypoints_1.append(keypoints)

im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0, 0, 255),
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
heatmap1 = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(heatmap1, 125, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
print("thresh",thresh)
# thresh = cv2.threshold(heatmap1,127,255,0)
contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
cv2.CHAIN_APPROX_NONE)[0]
threshold_blob_area=10
print("contours",len(contours))
colors = [(0,255,0),(255,255,255),(0,0,255),(255,0,255),(255,0,0),(255,255,0)]
for i in range(1, len(contours)):
    # index_level = int(hierarchy[0][i][1])
    # if index_level<=i:
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        print("area",area)
        if area>threshold_blob_area:
            heatmap = cv2.drawContours(heatmap, [cnt], -1, colors[i], 3)

            # ellipse = cv2.fitEllipse(cnt)
            # heatmap = cv2.ellipse(heatmap, ellipse, (0, 255, 0), 2)




cv2.imshow("image",heatmap)
cv2.waitKey(100000000)
