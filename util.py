import cv2
import numpy as np
def mark_rect(mark, p1, p2, on=10, step=20, thick=1, color=(128, 128, 128)):
    # cv2.rectangle(mark, p1, p2, color,thick)

    for x in range(p1[0], p2[0], step):
        cv2.line(mark, (x, p1[1]), (x + on, p1[1]), color, thick)
        cv2.line(mark, (x, p2[1]), (x + on, p2[1]), color, thick)

    for y in range(p1[1], p2[1], step):
        cv2.line(mark, (p1[0], y), (p1[0], y + on), color, thick)
        cv2.line(mark, (p2[0], y), (p2[0], y + on), color, thick)


def yellow_marker(image, x1, y1, x2, y2):
    rect = image[x1:x2, y1:y2]

    # Create a yellow color
    yellow = (128, 255, 255)

    # Create a mask for only white pixels
    mask = np.all(rect == [255, 255, 255], axis=-1)

    # Apply the yellow color to the white pixels
    rect[mask] = yellow

def image_cells(image, factor):

    width=image.shape[0]
    height=image.shape[1]

    scaled_width=width//factor
    scaled_height=height//factor



    result=np.zeros( ( scaled_width ,scaled_height), np.uint8)

    for x in range(0,scaled_width):
        for y in range(0,scaled_height):
            m=np.mean(image[x * factor:(x + 1) * factor, y * factor:(y + 1) * factor])

            result[x][y]=m

    return result
