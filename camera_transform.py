import os
import cv2
from base_camera import BaseCamera


class CameraTransform(BaseCamera):
    """crops/scews input stream"""
    input_camera:BaseCamera=None

    def __init__(self, input_camera:BaseCamera):
        CameraTransform.input_camera=input_camera
        super(CameraTransform, self).__init__()


    @staticmethod
    def frames():

        while True:
            frame=CameraTransform.input_camera.get_frame()

            #scew
            # cv2.transform()
            # M = cv2.getPerspectiveTransform(pts1, pts2)
            # dst = cv2.warpPerspective(img, M, (cols, rows))

            # encode as a jpeg image and return it
            # yield cv2.imencode('.jpg', img)[1].tobytes()
            yield frame