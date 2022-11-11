import os
import cv2
from base_camera import BaseCamera


class CameraOpenCV(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            CameraOpenCV.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(CameraOpenCV, self).__init__()

    @staticmethod
    def set_video_source(source):
        CameraOpenCV.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(CameraOpenCV.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()


            # yield raw frames for further processing
            yield img
