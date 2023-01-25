import glob
import time
from typing import List, Iterator

import cv2

from camera import Camera

class CameraTest(Camera):


    def __init__(self):
        super().__init__()

        self.files = glob.glob("test/*.png")
        self.files.sort()
        self.file_nr=0

        # #start
        # while self.files.pop(0) != "test/1670449545.png":
        #         pass
        #
        # #loop
        # while self.files.pop() != "test/1670449735.png":
        #         pass
        #

        # while self.files.pop(0)!="test/1670449338.png":
        while self.files.pop(0) != "test/1670449545.png":
                pass


    def get_frame(self):
        # time.sleep(1)
        self.file_nr=(self.file_nr+1)%len(self.files)
        print("Image {}".format(self.files[self.file_nr]))
        return cv2.imread(self.files[self.file_nr])

