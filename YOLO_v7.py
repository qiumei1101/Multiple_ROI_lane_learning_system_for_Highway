import sys
# relative_darknet_path = "../" #Comment this if darknet.py is in the same directory as this file
# sys.path.append(relative_darknet_path)
relative_darknet_path = "../yolov7" #Comment this if darknet.py is in the same directory as this file

# relative_darknet_path = "../yolov5_attention" #Comment this if darknet.py is in the same directory as this file
sys.path.append(relative_darknet_path)
# print("relative_darknet_path",relative_darknet_path)
from pathlib import Path
import cv2
import torch.backends.cudnn as cudnn
from numpy import random
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages, letterbox
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel
import numpy as np
import torch
import os
half = False
import time

classify = False
trace = False
class YOLO_darknet:
    def __init__(self):
        self.weights = 'yolov7x.pt'
        # self.weights = 'runs/train/exp_defalut_hyp_300_yolov5x_2cbam_next400eph_betterperformance_third_train/weights/best.pt'
        self.conf_thres = 0.25
        self.iou_thres= 0.45
        self.data = 'data/coco.yaml'
        self.device = 'cuda:0'
        self.augment = False
        self.visualize = False
        self.img_size=640
        self.auto = True
        self.max_det = 1000
        self.agnostic_nms = False
        self.classes = None

        # Load model
        # Initialize
        set_logging()
        self.device = select_device(self.device)
        half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(self.img_size, s=self.stride)  # check img_size
        # if trace:
        #     model = TracedModel(model, device, opt.img_size)

        # if half:
        #     self.model.half() # to FP16

            # Second-stage classifier

        if classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model']).to(self.device).eval()

            # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        # print("  self.names",  self.names)
        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters()))) # run once

    cwd = os.getcwd()
    os.chdir(relative_darknet_path)
    def classify(self, frame):
        # Padded resize
        prev_time = time.time()
        img = letterbox(frame, self.imgsz, stride=self.stride)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        # t1 = time_synchronized()

        pred = self.model(img, augment=self.augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic_nms)
        # t2 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, self.modelc, img, frame)

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
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                # # Print results
                # for c in det[:, -1].unique():
                #     # print("c",c,"det",det)
                #     n = (det[:, -1] == c).sum()  # detections per class
                # #     # s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                xywhs = xyxy2xywh(det[:, 0:4])
                confs = det[:, 4]
                clss = det[:, 5]
                xywh = xywhs.tolist()
                confs = confs.tolist()
                clss = clss.tolist()
                # print("clss",clss)
                for xyxy in xywh:
                    if clss[xywh.index(xyxy)]==2.0 or clss[xywh.index(xyxy)]==7.0:
                        if clss[xywh.index(xyxy)]==2.0:
                            label ='car'
                        else:
                            label = 'truck'
                        detection_list.append([label, confs[xywh.index(xyxy)], int(xyxy[0]-xyxy[2]/2), int(xyxy[1]-xyxy[3]/2), int(xyxy[2]), int(xyxy[3])])
                        boxes_list.append([int(xyxy[0]-xyxy[2]/2), int(xyxy[1]-xyxy[3]/2), int(xyxy[2]), int(xyxy[3])])
                        confidence.append(confs[xywh.index(xyxy)])
                        classes.append(label)
                        ratios.append(xyxy[2]/xyxy[3])

            return detection_list, boxes_list, confidence, ratios, classes, fps