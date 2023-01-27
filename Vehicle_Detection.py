
import cv2
import numpy as np
def vehicle_detection_engine(classifier,collect_det_dots_including_truck,
                collect_cars, frame,
                             frame_id):
    detections, boxs, scores, class_names, fps = classifier.classify(frame)
    iii = 0
    for box in boxs:
        if 10 < box[2] < 550 and 10 < box[3] < 550:
            if class_names[iii] == 'car':
                collect_cars.append(
                    (box[0] + int(box[2] / 2), box[1] + int(box[3] / 2), box[2], box[3], frame_id, scores[iii]))
            if class_names[iii] == 'car' or class_names[iii] == 'truck':
                collect_det_dots_including_truck.append(
                    (box[0] + int(box[2] / 2), box[1] + int(box[3] / 2), int(box[2]/4*3), box[3], frame_id, scores[iii]))
            cv2.rectangle(frame,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(0,255,255),2)

        iii += 1

    return collect_det_dots_including_truck, collect_cars,frame

def Vehicle_Detection_in_continuous_learning(video,classifier,collect_det_dots_including_truck,
                collect_cars,vehicle_collected,count):

    ret, frame = video.read()

    if not vehicle_collected:
        ret, frame = video.read()
        if (type(frame) is np.ndarray):

            collect_det_dots_including_truck,collect_cars,frame=vehicle_detection_engine(classifier,collect_det_dots_including_truck,
                collect_cars,frame,count)
            # cv2.imshow("frame", frame)
            # cv2.waitKey(1)

    return collect_det_dots_including_truck,collect_cars,frame

