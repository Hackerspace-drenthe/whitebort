import os
import cv2
from base_camera import BaseCamera


class CameraOpenCV(BaseCamera):

    def __init__(self):
        self.video_source = 0

        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            self.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(CameraOpenCV, self).__init__()

    def set_video_source(self,source):
        self.video_source = source

    def frames(self):
        camera = cv2.VideoCapture(self.video_source)

        camera.set(cv2.CAP_PROP_FPS,1)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()


            # yield raw frames for further processing
            yield img
