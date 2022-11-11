import io
import time
import picamera
import numpy

from camera import Camera


class CameraPi(Camera):

    def __init__(self, **kwargs):
        self.x_res=1920
        self.y_res=1088
        # x_res*=2
        # y_res*=2
        #
        # HQ cam
        # x_res=4056
        # y_res=3040

        self.camera=picamera.PiCamera()
        self.camera.resolution = (x_res, y_res)
        self.camera.framerate = 1

    def get_frame(self):

        image = numpy.empty((self.y_res * self.x_res * 3,), dtype=numpy.uint8)
        self.camera.capture(image, 'bgr')
        image = image.reshape((self.y_res, self.x_res, 3))
        return image
