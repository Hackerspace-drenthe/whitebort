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

            top_left_factor=(0.272, 0.281)
            top_right_factor=(0.741, 0.04)
            bottom_left_factor=(0.098, 0.988)
            bottom_right_factor=(0.98,0.723)


            rows, cols, ch = input_frame.shape
            top_left=[int(cols * top_left_factor[0]), int(rows * top_left_factor[1])]
            top_right=[int(cols * top_right_factor[0]), int(rows * top_right_factor[1])]
            bottom_left=[int(cols * bottom_left_factor[0]), (rows * bottom_left_factor[1])]
            bottom_right=[int(cols * bottom_right_factor[0]), int(rows * bottom_right_factor[1])]

            # cv2.line(input_frame, top_left, top_right , (0,255,0),1)
            # cv2.line(input_frame, top_left, top_right , (0,255,0),1)
            # cv2.line(input_frame, top_left, top_right , (0,255,0),1)
            # cv2.line(input_frame, top_left, top_right , (0,255,0),1)

            polypts = numpy.array([
                top_left,
                 top_right,
                 bottom_right,
                bottom_left,
            ], numpy.int32)
            cv2.polylines(input_frame, [polypts], True, (0,255,0))

            pts1 = numpy.float32(
                [
                    top_left,
                    top_right,
                    bottom_right,
                    bottom_left,
                ])

            target_top_left=top_left
            target_top_right=(top_right[0], top_left[1])
            target_bottom_left=(top_left[0], bottom_left[1])
            target_bottom_right=(top_right[0], bottom_left[1])

            pts2 = numpy.float32(
                [
                    target_top_left,
                    target_top_right,
                    target_bottom_right,
                    target_bottom_left
                 ]
            )
            #scew
            M = cv2.getPerspectiveTransform(pts1, pts2)
            result = cv2.warpPerspective(input_frame, M, (cols, rows))


            yield result
            # yield input_frame