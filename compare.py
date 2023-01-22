import sys

import cv2
import numpy

import settings
from util import yellow_marker, image_cells


# Current algorithm:
# - scale images down by a huge factor so that each pixel represents a 'cell' with the average value of that cell.
# - absdiff both lowres images
# - calculate mean absdiff
# - determine change factor of each cell compared to mean absdiff
# - if change factor is above or below a certain threshold, we set or clear the change status in our grid.

# This should also be resilient to noise etc

class Compare:

    def __init__(self):

        self.grid = None
        self.width = None
        self.height = None

    def create(self, width, height):
        self.height = height
        self.width = width
        self.clear(

        )

    def clear(self):
        if self.width:
            self.grid = numpy.zeros((self.width // settings.compare_factor, self.height // settings.compare_factor),
                                    bool)

    def get_changes(self):

        changes = 0
        for col in self.grid:
            for cell in col:
                if cell:
                    changes = changes + 1
        return changes

    def update(self, before: numpy.ndarray, after: numpy.ndarray):
        """compare before and after, and update our change-grid. returns number of changes made to the grid this time."""

        if self.grid is None:
            self.create(before.shape[0], before.shape[1])

        # scale down by this factor. We will compare per 'cell'
        # before_scaled = cv2.resize(before, (
        # before.shape[1] // settings.compare_factor, before.shape[0] // settings.compare_factor), 0,0, cv2.INTER_AREA )
        before_scaled=image_cells(before, settings.compare_factor)

        # after_scaled = cv2.resize(after, (
        # before.shape[1] // settings.compare_factor, before.shape[0] // settings.compare_factor),0,0, cv2.INTER_AREA)
        after_scaled=image_cells(after, settings.compare_factor)

        # cv2.imwrite("test.png", before_scaled)
        # sys.exit()

        differences = cv2.absdiff(before_scaled, after_scaled)
        # print("diff cells", (differences[10]))


        mean_differences = cv2.mean(differences)  # per chan\


        mean_difference = 0
        for d in mean_differences:
            mean_difference = mean_difference + d

        changes = 0

        # get differences that are over the threshold, compare to the average change of all the cells.
        print("shapes ", differences.shape)
        for x in range(0, differences.shape[0]):
            for y in range(0, differences.shape[1]):
                diff = 0
                # for channel_nr in range(0, 3):
                #     diff = diff + differences[y][x][channel_nr]

                # diff_factor = abs(diff - mean_difference) / (255 * 3)
                # diff_factor = diff / (255 * 3)
                diff_factor=differences[x][y]/255

                # over threshold, flip cell to 'changed'
                if diff_factor >= settings.compare_dirty_threshold and not self.grid[x][y]:
                    self.grid[x][y] = True
                    changes = changes + 1
                # under threshold, flip cell to 'unchanged'
                elif diff_factor <= settings.compare_clean_threshold and self.grid[x][y]:
                    self.grid[x][y] = False
                    changes = changes + 1

        return (changes)

    def mark(self, image: numpy.ndarray):
        """mark differences in image"""

        print("GRIDSHAPE", self.grid.shape)
        print("is" , self.grid.shape[0]*settings.compare_factor)

        for x in range(0, self.grid.shape[0]):
            for y in range(0, self.grid.shape[1]):
                if self.grid[x][y]:
                    yellow_marker(image, x * settings.compare_factor, y * settings.compare_factor,
                                  (x + 1) * settings.compare_factor, (y + 1) * settings.compare_factor)
