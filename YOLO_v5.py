import sys
relative_darknet_path = "../" #Comment this if darknet.py is in the same directory as this file
sys.path.append(relative_darknet_path)
relative_darknet_path = "../yolov5" #Comment this if darknet.py is in the same directory as this file

# relative_darknet_path = "../yolov5_attention" #Comment this if darknet.py is in the same directory as this file
sys.path.append(relative_darknet_path)

from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.augmentations import Albumentations, augment_hsv, copy_paste, letterbox, mixup, random_perspective
import numpy as np
import torch
import os
half = False
import time
class YOLO_darknet:
    def __init__(self):
        self.imgsz = (640, 640)
        self.weights = 'yolov5x.pt'

        # self.weights = 'runs/train/exp_defalut_hyp_300_yolov5x_2cbam_next400eph_betterperformance_third_train/weights/best.pt'
        self.conf_thres = 0.25
        self.iou_thres= 0.45
        self.data = 'data/coco128.yaml'
        self.device = ''
        self.augment = False
        self.visualize = False
        self.img_size=640
        self.auto = True
        self.max_det = 1000
        self.agnostic_nms = False
        self.classes = None

        # Load model
        self.device = select_device(self.device)
        self.model = DetectMultiBackend(self.weights, device=self.device, dnn=False, data=self.data, fp16=half)
        self.stride, self.names, self.pt = self.model.stride,  self.model.names,  self.model.pt
        # print("pt", self.pt)
        imgsz = check_img_size(self.imgsz, s=self.stride)  # check image size

    cwd = os.getcwd()
    os.chdir(relative_darknet_path)
    def classify(self, frame):
        # Padded resize
        prev_time = time.time()
        img = letterbox(frame, self.img_size, stride=self.stride, auto=self.auto)[0]

        # Convert
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)
        im = torch.from_numpy(img).to(self.device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch
        pred = self.model(im, augment=self.augment, visualize=self.visualize)
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)

        fps = int(1 / (time.time() - prev_time))
        print("FPS: {}".format(fps))
        detection_list = []
        boxes_list = []
        confidence = []
        classes = []
        ratios = []
        # print("lenpred",len(pred))
        for i, det in enumerate(pred):  # detections per image
            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], frame.shape).round()
                # # Print results
                for c in det[:, -1].unique():
                    # print("c",c,"det",det)
                    n = (det[:, -1] == c).sum()  # detections per class
                #     # s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                xywhs = xyxy2xywh(det[:, 0:4])
                confs = det[:, 4]
                clss = det[:, 5]
                xywh = xywhs.tolist()
                confs = confs.tolist()
                clss = clss.tolist()
                # print("clss",clss)
                for xyxy in xywh:
                    if int(clss[xywh.index(xyxy)])==7 or int(clss[xywh.index(xyxy)])==2:
                        if clss[xywh.index(xyxy)]==2:
                            label ='car'
                        else:
                            label = 'truck'
                        detection_list.append([label, confs[xywh.index(xyxy)], int(xyxy[0]-xyxy[2]/2), int(xyxy[1]-xyxy[3]/2), int(xyxy[2]), int(xyxy[3])])
                        boxes_list.append([int(xyxy[0]-xyxy[2]/2), int(xyxy[1]-xyxy[3]/2), int(xyxy[2]), int(xyxy[3])])
                        confidence.append(confs[xywh.index(xyxy)])
                        classes.append(label)


            return detection_list, boxes_list, confidence, classes, fps