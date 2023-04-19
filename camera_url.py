import time

import cv2
import numpy as np
import requests as requests

from camera import Camera

class CameraURL(Camera):

    def __init__(self, url):
        super().__init__()
        self.url=url
        # self.frame_delay=frame_delay

    def get_frame(self):
        while True:
            try:
                resp = requests.get(self.url, stream=True, timeout=10).raw
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                frame=cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
                # time.sleep(self.frame_delay)
                return  frame
            except Exception as e:
                print("ERROR: while gettinging frame: {}".format(str(e)))

            time.sleep(5)

