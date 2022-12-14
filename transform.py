import os
import cv2
import numpy
from settings import top_left_factor, top_right_factor, bottom_left_factor, bottom_right_factor

def transform(input_frame):
    """crops/scews image"""


    rows, cols, ch = input_frame.shape
    top_left = [int(cols * top_left_factor[0]), int(rows * top_left_factor[1])]
    top_right = [int(cols * top_right_factor[0]), int(rows * top_right_factor[1])]
    bottom_left = [int(cols * bottom_left_factor[0]), (rows * bottom_left_factor[1])]
    bottom_right = [int(cols * bottom_right_factor[0]), int(rows * bottom_right_factor[1])]

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
    cv2.polylines(input_frame, [polypts], True, (0, 255, 0))

    #set source of the transform
    pts1 = numpy.float32(
        [
            top_left,
            top_right,
            bottom_right,
            bottom_left,
        ])

    #set target of transform (upper left, straightened)
    offset_x = top_left[0]
    offset_y = top_left[1]

    target_top_left = (0, 0)
    target_top_right = (top_right[0] - offset_x, top_left[1] - offset_y)
    target_bottom_left = (top_left[0] - offset_x, bottom_left[1] -offset_y)
    target_bottom_right = (top_right[0] - offset_x, bottom_left[1]- offset_y)

    pts2 = numpy.float32(
        [
            target_top_left,
            target_top_right,
            target_bottom_right,
            target_bottom_left
        ]
    )

    #zoom to fit, keeping aspect
    zoom=cols/target_bottom_right[0]

    pts2*=zoom

    #do actual transform
    M = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(input_frame, M, (int(target_bottom_right[0]*zoom),int(target_bottom_right[1]*zoom)))


    return result
    # yield input_frame
