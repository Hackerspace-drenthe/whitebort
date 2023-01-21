import cv2
import numpy
import numpy as np
from skimage.metrics import structural_similarity

import settings



def mark_rect(mark, p1, p2, on=10, step=20, thick=1, color=(128, 128, 128)):
    # cv2.rectangle(mark, p1, p2, color,thick)


    for x in range(p1[0], p2[0], step):
        cv2.line(mark, (x, p1[1]), (x + on, p1[1]), color, thick)
        cv2.line(mark, (x, p2[1]), (x + on, p2[1]), color, thick)

    for y in range(p1[1], p2[1], step):
        cv2.line(mark, (p1[0], y), (p1[0], y + on), color, thick)
        cv2.line(mark, (p2[0], y), (p2[0], y + on), color, thick)


def yellow_marker(image, x1,y1,x2,y2):

    rect=image[y1:y2, x1:x2]

    # Create a yellow color
    yellow = (128, 255,255)

    # Create a mask for only white pixels
    mask = np.all(rect == [255, 255, 255], axis=-1)

    # Apply the yellow color to the white pixels
    rect[mask] = yellow




def compare(before: numpy.ndarray, after, mark=None):
    """compare before and after, and mark differces in mark. returns number of differences """

    # scale down by this factor. We will compare per 'cell'
    factor = 20
    before_scaled = cv2.resize(before, (int(before.shape[1] / factor), int(before.shape[0] / factor)))
    after_scaled = cv2.resize(after, (int(before.shape[1] / factor), int(before.shape[0] / factor)))

    differences = cv2.absdiff(before_scaled, after_scaled)
    mean_difference = cv2.mean(differences)  # per chan

    threshold_factor = 0.05

    # print(differences)
    count = 0
    # get differences that are over the threshold, compare to the average change of all the cells.
    for x in range(0, differences.shape[1]):
        for y in range(0, differences.shape[0]):
            for channel_nr in range(0, 3):
                diff = abs(differences[y][x][channel_nr] - mean_difference[channel_nr]) / 255
                if (diff > threshold_factor):
                    count = count + 1
                    if mark is not None:
                        # mark_rect(mark, (x * factor, y * factor), ((x + 1) * factor, (y + 1) * factor))
                        yellow_marker(mark, x * factor, y * factor, (x + 1) * factor, (y + 1) * factor)

    return count
