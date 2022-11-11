import os
import time

import cv2

from camera import Camera


class CameraOpenCV(Camera):

    def __init__(self, **kwargs):
        self.video_source = 0

        self.camera = cv2.VideoCapture(self.video_source)

        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')

        self.camera.set(cv2.CAP_PROP_FPS, 1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


    def get_frame(self):

        _, img = self.camera.read()

        return img
        # time.sleep(self.frame_delay)
