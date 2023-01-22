import threading
import time

import settings
import transform
import whiteboardenhance
from camera import Camera
from clientevent import ClientEvent
import compare
import cv2
import os

from telegram_bot import TelegramBot


class Whitebort(object):

    def __init__(self, camera: Camera, bot: TelegramBot):

        self.camera = camera
        self.bot = bot
        self.thread = None  # background thread that reads frames from camera
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()
        self.compare= compare.Compare()

        self.frames = {
            'input': None,  # raw input frame from cam
            'transform': None,  # transformed frame (cropping, skew, rotate, mirror etc)
            'whiteboardenhance': None,  # transformed AND enchanged with whiteboard filter

            'sent_whiteboardenhance': None,  # last sent frames to telegram
            'sent_transform': None

        }

        # if os.path.isfile(settings.sent_transform_frame_file):
        #     self.frames['sent_transform'] = cv2.imread(settings.sent_transform_frame_file)
        # else:
        #     print("ERROR: {} not found!".format(settings.sent_transform_frame_file))

        """Start the background camera thread if it isn't running yet."""
        self.last_access = time.time()

        # start background frame thread
        self.thread = threading.Thread(target=self._thread)
        self.thread.start()

        # self.input_frame = []

    def get_frames(self, wait=True):
        """Wait until a frame is processed and get all in-between processing steps"""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        if wait:
            self.event.wait()
            self.event.clear()

        return self.frames

    def process_frame(self):
        """get next frame, do processing and store in self"""

        frame=self.camera.get_frame()
        if frame is None:
            return

        self.frames['input'] = frame
        self.event.set()

        if settings.save and settings.mode != "test":
            cv2.imwrite(f"{int(time.time())}.png", self.frames['input'])

        self.frames['transform'] = transform.transform(self.frames['input'])
        self.frames['whiteboardenhance'] = whiteboardenhance.whiteboard_enhance(self.frames['transform'])

    def send(self):
        """send current frames and store for next comparison"""

        change_count = self.compare.get_changes()
        print("Sending {} actual changes to telegram.".format(change_count))
        cv2.putText(self.frames['whiteboardenhance'], "{} changes".format(change_count), (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

        self.frames['sent_transform'] = self.frames['transform']
        self.frames['sent_whiteboardenhance'] = self.frames['whiteboardenhance']

        cv2.imwrite(settings.sent_transform_frame_file, self.frames['sent_transform'])

        # sent to telegram
        if self.bot:
            telegram_file = "telegram.png"
            cv2.imwrite(telegram_file, self.sent_whiteboardenhance_frame)
            self.bot.send_message_image(telegram_file)

    def wait_for_stable_change(self):
        """process frames and wait until a change is stable
        """

        # self.process_frame()


        # last_frame = self.frames['transform']
        last_change_time = time.time()
        last_sent_change_count = 0

        while True:
            self.process_frame()
            now = time.time()

            if self.frames['sent_transform'] is None:
                self.frames['sent_transform'] = self.frames['transform']

            # changes compared to last frame?
            # change_count = compare.compare(self.frames['transform'], last_frame, self.frames['whiteboardenhance'])
            # if change_count:
            #     print("Movement detected: {} changes.".format(change_count))
            #     last_change_time = now
            # no changes to last sent frame? or number of changes has changed?

            changes=self.compare.update(self.frames['sent_transform'], self.frames['transform'])
            print(changes, self.compare.get_changes())

            self.compare.mark(self.frames['whiteboardenhance'])

            if changes==0 and self.compare.get_changes()>0:
                return

            # if change_count == 0 or change_count != last_sent_change_count:
            #     if change_count != last_sent_change_count:
            #         print("Unstable changes: {} (was {})".format(change_count, last_sent_change_count))
            #     elif change_count == 0:
            #         print("No changes")
            #
            #     last_change_time = now
            #     last_sent_change_count = change_count
            #
            # no_change_time = int(now - last_change_time)
            # if no_change_time > settings.no_change_time:
            #     print("Stable change detected!".format(settings.no_change_time))
            #     return
            # else:
            #     if no_change_time > 0:
            #         print(
            #             "Board has {} stable changes for {} seconds. (waiting {}s)".format(change_count, no_change_time,
            #                                                                                settings.no_change_time))
            #
            # last_frame = self.frames['transform']

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        while True:
            self.wait_for_stable_change()
            self.send()
            # self.compare_and_send()
