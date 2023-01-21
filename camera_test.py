import glob
import time
from typing import List, Iterator

import cv2

from camera import Camera

# files=[
#     "1670423174",
#     "1670423175",
#     "1670423176",
#     "1670423177", #hand
#
#     "1670423182",
#     "1670423183",
#     "1670423184",
#     "1670423185",
# ]


class CameraTest(Camera):


    def __init__(self):
        super().__init__()

        self.files = glob.glob("test/*.png")
        self.files.sort()
        self.file_nr=0


    def get_frame(self):
        # time.sleep(1)
        self.file_nr=(self.file_nr+1)%len(self.files)
        print("Image {}".format(self.files[self.file_nr]))
        return cv2.imread(self.files[self.file_nr])

