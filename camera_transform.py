import os
import cv2
from base_camera import BaseCamera
import numpy

class CameraTransform(BaseCamera):
    """crops/scews input stream"""

    def __init__(self, input_camera:BaseCamera):
        self.input_camera=input_camera
        super().__init__()


    def frames(self):

        while True:
            input_frame=self.input_camera.get_frame()

            rows, cols, ch = input_frame.shape
            pts1 = numpy.float32(
                [[cols * .25, rows * .95],
                 [cols * .90, rows * .95],
                 [cols * .10, 0],
                 [cols, 0]]
            )
            pts2 = numpy.float32(
                [[cols * 0.5, rows],
                 [cols, rows],
                 [0, 0],
                 [cols, 0]]
            )
            #scew
            M = cv2.getPerspectiveTransform(pts1, pts2)
            result = cv2.warpPerspective(input_frame, M, (cols, rows))

            # encode as a jpeg image and return it
            # yield cv2.imencode('.jpg', img)[1].tobytes()
            yield result