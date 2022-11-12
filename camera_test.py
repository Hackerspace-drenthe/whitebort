import time

import cv2

from camera import Camera


class CameraTest(Camera):

    def __init__(self):
        super().__init__()
        self.imgs = [cv2.imread(f + '.png') for f in ['2','3', '4']]
        self.frame_nr=0


    def get_frame(self):
        time.sleep(1)
        self.frame_nr=(self.frame_nr+1)%len(self.imgs)
        print("Framenr {}".format(self.frame_nr))
        return  self.imgs[self.frame_nr]

