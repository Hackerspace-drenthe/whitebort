import time

import cv2

from camera import Camera

files=[
    "1670423174",
    "1670423175",
    "1670423176",
    "1670423177", #hand

    "1670423182",
    "1670423183",
    "1670423184",
    "1670423185",
]

class CameraTest(Camera):

    def __init__(self):
        super().__init__()
        self.imgs = [cv2.imread(f + '.png') for f in files]
        self.frame_nr=0


    def get_frame(self):
        time.sleep(1)
        self.frame_nr=(self.frame_nr+1)%len(self.imgs)
        print("Image {}".format(files[self.frame_nr]))
        return  self.imgs[self.frame_nr]

