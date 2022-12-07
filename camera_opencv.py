import os
import time

import cv2

from camera import Camera


class CameraOpenCV(Camera):

    def __init__(self, **kwargs):
        self.video_source = 0

        self.camera = cv2.VideoCapture(self.video_source)
        time.sleep(3)

        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')

        self.camera.set(cv2.CAP_PROP_FPS, 1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.camera.set(cv2.CAP_PROP_AUTO_WB, 0.0)
        self.camera.set(cv2.CAP_PROP_WB_TEMPERATURE, 4200)

        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)
        self.camera.set(cv2.CAP_PROP_EXPOSURE, 0.0)
        self.camera.set(cv2.CAP_PROP_GAIN, 0.0)
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0.0)


    def get_frame(self):

        _, img = self.camera.read()

        return img
        # time.sleep(self.frame_delay)
