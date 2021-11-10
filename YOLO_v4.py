import os
import cv2
import numpy as np
import random
import time

import sys
relative_darknet_path = "../../darknet_master" #Comment this if darknet.py is in the same directory as this file
sys.path.append(relative_darknet_path) #Comment this if darknet.py is in the same directory as this file
import darknet #Ignore the import warning if darknet.py is in ../<"directory-name">


class YOLO_darknet:
    def __init__(self):

        self.config_file = "cfg/yolov4.cfg"
        self.data_file = "cfg/coco.data"
        # self.input_size = 320
        self.weights = "yolov4.weights"
        self.thresh = .20
        self.netMain = None
        self.metaMain = None
        ################################################################
        #
        #   Do not remove the next two lines of code
        #   The source code (including this) should be in a subdirectory under a directory that contains the darknet-master files.
        #   i.e. This will search one level above the current working directory for the necessary files.
        #
        #################################################################
        cwd = os.getcwd()
        os.chdir(relative_darknet_path)
        ####################################################################
        self.network, self.class_names, self.class_colors = darknet.load_network(
            self.config_file,
            self.data_file,
            self.weights,
            batch_size=1
        )

        if self.netMain is None:
            self.netMain = darknet.load_net_custom(self.config_file.encode("ascii"), self.weights.encode("ascii"), 0,
                                                   1)  # batch size = 1
        if self.metaMain is None:
            self.metaMain = darknet.load_meta(self.data_file.encode("ascii"))

        # Darknet doesn't accept numpy images.
        # Create one with image we reuse for each detect
        self.width = darknet.network_width(self.network)
        self.height = darknet.network_height(self.network)

        self.darknet_image = darknet.make_image(self.width, self.height, 3)
        assert 0 < self.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
        if not os.path.exists(self.config_file):
            raise (ValueError("Invalid config path {}".format(os.path.abspath(self.config_file))))
        if not os.path.exists(self.weights):
            raise (ValueError("Invalid weight path {}".format(os.path.abspath(self.weights))))
        if not os.path.exists(self.data_file):
            raise (ValueError("Invalid data file path {}".format(os.path.abspath(self.data_file))))
        os.chdir(cwd) # Do not remove
    def classify(self, frame):
        bgr_img = frame[:, :, ::-1]
        height, width = bgr_img.shape[:2]

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_resized = cv2.resize(frame_rgb, (self.width, self.height), interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())
        prev_time = time.time()
        detections = darknet.detect_image(self.network, self.class_names, self.darknet_image, thresh=self.thresh)
        fps = int(1 / (time.time() - prev_time))
        # print("FPS: {}".format(fps))
        detection_list = []
        boxes_list = []
        confidence = []
        classes = []

        for detection in detections:
            x, y, w, h = detection[2][0], \
                         detection[2][1], \
                         detection[2][2], \
                         detection[2][3]
            conf = detection[1]
            x *= width / darknet.network_width(self.netMain)
            w *= width / darknet.network_width(self.netMain)
            y *= height / darknet.network_height(self.netMain)
            h *= height / darknet.network_height(self.netMain)
            xyxy = np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])

            label = detection[0]
            conf = float(conf) / 100
            conf = round(conf, 2)
            # if label=='person':
            if label == "train":
                label = "truck"
            # if label == "car" or label == "truck" or label == "bus" or:
            detection_list.append([label, conf, int(xyxy[0]), int(xyxy[1]), int(w), int(h)])
            boxes_list.append([int(xyxy[0]), int(xyxy[1]), int(w), int(h)])
            confidence.append(conf)
            classes.append(label)

        return detection_list, boxes_list, confidence, classes, fps
