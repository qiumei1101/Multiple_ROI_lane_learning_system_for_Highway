# It is a automatically lane learning system which can generate multiple ROIs based on vehicle detection confidence score on highway videos.it can work on both online cameras and local videos.

## System information of this code is tested on:
OS: Ubuntu 20.04.6 LTS, 64-bit
CPU: Intel® Core™ i7-9800X CPU @ 3.80GHz × 16 
GPU: NVIDIA Corporation TU104GL [Quadro RTX 5000]
CUDA version: 12.1


## Preparation

To run this project, you will need to:

      1. install Yolov7 following the guildance https://github.com/WongKinYiu/yolov7.git or install any other detectors
        
      2. install Python 3 and Anaconda. 
      



## Installation

Please download the project into the same folder path with installed Yolov7 or Yolov3, Yolov4, Yolov5

```bash
  git clone https://github.com/qiumei1101/Multiple_ROI_lane_learning_system_for_Highway.git
  cd Multiple_ROI_lane_learning_system_for_Highway
  conda env create -f environment.yml
```

## Running Tests

To run tests, run the following command

```bash
  python MROI_Lane_Learning_System.py --video_path='rtsp://10.6.25.24' --saving_path='/home/meiqiu@ads.iu.edu/
  JTRP_project/Multiple_ROI_lane_learning_system_for_Highway/results/' --detector='YOLO_v7' 
  #here you can replace the camera id with any camera ip you plan to test
```
```bash
  #use the following command for recorded video
  python MROI_Lane_Learning_System.py --video_path='/media/meiqiu/CA8C57E38C57C919/MEIREQUESTEDVIDEOS/sunny/1-065-115-5-1+2020-09-05+14.42.mp4' --saving_path='/home/meiqiu@ads.iu.edu/JTRP_project/Multiple_ROI_lane_learning_system_for_Highway/results/' --detector='YOLO_v7' 
```

# The final lane learning result will be:
![alt text](./results/1-465-008-2-1+2020-08-10+14.50/1_lane_learning_in_multiple_ROI.png?raw=true)
```bash
  @article{qiu2024intelligent,
  title={Intelligent Highway Adaptive Lane Learning System in Multiple ROIs of Surveillance Camera Video},
  author={Qiu, Mei and Christopher, Lauren and Chien, Stanley Yung-Ping and Chen, Yaobin},
  journal={IEEE Transactions on Intelligent Transportation Systems},
  year={2024},
  publisher={IEEE}
}
```

