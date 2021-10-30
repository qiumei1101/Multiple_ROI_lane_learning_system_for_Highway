import YOLO_v4 as YOLOV4
import cv2
import ConfigCustom
classifier = YOLOV4.YOLO_darknet()
video = cv2.VideoCapture(ConfigCustom.FILE)
collect_cars=[]
collect_det_dots_including_truck=[]
def vehicle_detection_engine(classifier, frame,
                             frame_id):
    detections, boxs, scores, class_names, fps = classifier.classify(frame)

    iii = 0
    for box in boxs:
        if 10 < box[2] < 450 and 10 < box[3] < 450:
            if class_names[iii] == 'car':
                collect_cars.append(
                    (box[0] + int(box[2] / 2), box[1] + int(box[3] / 2), box[2], box[3], frame_id, scores[iii]))
            if class_names[iii] == 'car' or class_names[iii] == 'truck':
                collect_det_dots_including_truck.append(
                    (box[0] + int(box[2] / 2), box[1] + int(box[3] / 2), box[2], box[3], frame_id, scores[iii]))
            cv2.rectangle(frame,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(0.255,255),2)
            cv2.imshow("frame",frame)
            cv2.waitKey(1)
        iii += 1

    return collect_det_dots_including_truck, collect_cars,frame

def Vehicle_Detection_in_continuous_learning(vehicle_collected,count):
    video_recording = True
    camera_angle_changed_ELS=False
    ret, frame = video.read()
    global  collect_det_dots_including_truck,collect_cars
    if vehicle_collected:
        video_recording = False
    while not vehicle_collected:
        ret, frame = video.read()
        collect_det_dots_including_truck,collect_cars,frame=vehicle_detection_engine(classifier,frame,count)

    return collect_det_dots_including_truck,collect_cars,frame,camera_angle_changed_ELS

