import io
import time
import picamera
from whitebort import Whitebort
import numpy


class CameraPi(Whitebort):
    @staticmethod
    def frames():

        #HD
        x_res=1920
        y_res=1088
        # x_res*=2
        # y_res*=2
        #
        # HQ cam
        # x_res=4056
        # y_res=3040
        with picamera.PiCamera() as camera:

            camera.resolution = (x_res, y_res)
            camera.framerate = 1
            time.sleep(2)

            while True:
                image = numpy.empty((y_res * x_res * 3,), dtype=numpy.uint8)
                camera.capture(image, 'bgr')
                image = image.reshape((y_res, x_res, 3))


                yield image
