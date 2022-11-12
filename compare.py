
import cv2
from skimage.metrics import structural_similarity



def mark_rect(mark, p1, p2, on=10, step=20, thick=1):

    for x in range(p1[0], p2[0], step):
        cv2.line(mark, (x, p1[1]), (x + on, p1[1]), (128, 128, 128), thick)
        cv2.line(mark, (x, p2[1]), (x + on, p2[1]), (128, 128, 128), thick)

    for y in range(p1[1], p2[1], step):
        cv2.line(mark, (p1[0], y), (p1[0], y + on), (128, 128, 128), thick)
        cv2.line(mark, (p2[0],y), (p2[0], y + on), (128, 128, 128), thick)


def compare(before, after, mark):
    """compare before and after, and mark differces in mark. returns similarity score """

    #winsize is belangrijk voor grootte van detectie
    win_size=5

    # Convert images to grayscale
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between the two images
    (score, diff) = structural_similarity(before_gray, after_gray, full=True, win_size=win_size)


    # The diff image contains the actual image differences between the two images
    # and is represented as a floating point data type in the range [0,1]
    # so we must convert the array to 8-bit unsigned integers in the range
    # [0,255] before we can use it with OpenCV
    diff = (diff * 255).astype("uint8")
    # diff_box = cv2.merge([diff, diff, diff])

    # Threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # mask = np.zeros(before.shape, dtype='uint8')
    # filled_after = after.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if area > 400:
            print("contour:", area)
            x, y, w, h = cv2.boundingRect(c)
            # cv2.rectangle(before, (x, y), (x + w, y + h), (36, 255, 12), 2)
            mark_rect(mark, (x, y), (x + w, y + h))
            # cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36, 255, 12), 2)
            # cv2.drawContours(mask, [c], 0, (255, 255, 255), -1)
            # cv2.drawContours(filled_after, [c], 0, (0, 255, 0), -1)

    # cv2.imshow('before', before)
    # cv2.imshow('after', after)
    # cv2.imshow('diff', diff)
    # cv2.imshow('thresh', thresh)
    # cv2.imshow('diff_box', diff_box)
    # cv2.imshow('mask', mask)
    # cv2.imshow('filled after', filled_after)
    # cv2.waitKey()


    return score