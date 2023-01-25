import threading
import time
from typing import Union

import numpy

import settings
import transform
import whiteboardenhance
from camera import Camera
from clientevent import ClientEvent
import compare
import cv2
import os

from telegram_bot import TelegramBot
from util import annotate


class Whitebort(object):

    def __init__(self, camera: Camera, bot: TelegramBot):

        self.camera = camera
        self.bot = bot
        self.thread = None  # background thread that reads frames from camera
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()
        self.compare = compare.Compare()

        self.frames: dict[str, Union[numpy.ndarray, None]] = {
            'input': None,  # raw input frame from cam
            'transform': None,  # step 1 transformed frame (cropping, skew, rotate, mirror etc)
            'filtered': None,  #  step 2 enchanged with whiteboard filter
            'annotated': None, #  step 3 annotations (marks and text)

            'sent_filtered': None,  # last sent frames to telegram
            'sent_annotated': None

        }

        if os.path.isfile(settings.last_sent_file):
            self.frames['sent_filtered'] = cv2.imread(settings.last_sent_file)
        else:
            print("ERROR: {} not found!".format(settings.last_sent_file))

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

        frame = self.camera.get_frame()
        if frame is None:
            return

        self.frames['input'] = frame
        self.event.set()

        if settings.save and settings.mode != "test":
            cv2.imwrite(f"{int(time.time())}.png", self.frames['input'])

        self.frames['transform'] = transform.transform(self.frames['input'])
        self.frames['filtered'] = whiteboardenhance.whiteboard_enhance(self.frames['transform'])
        self.frames['annotated'] = self.frames['filtered'].copy()

    def send(self):
        """send current frames out to the world"""

        # sent to telegram
        if self.bot:
            telegram_file = "telegram.png"
            cv2.imwrite(telegram_file, self.frames['sent_annotated'])
            self.bot.send_message_image(telegram_file)

    def wait_for_stable_change(self):
        """process frames and wait until a change is stable
        """

        # start with a clean comarison
        self.frames['sent_filtered'] = self.frames['filtered']
        self.compare.clear()

        stable_change_counter = 0
        while True:
            self.process_frame()

            current_changes = self.compare.update(self.frames['sent_filtered'], self.frames['filtered'])
            changes_since_sent = self.compare.get_changes()
            self.compare.mark(self.frames['annotated'])

            if current_changes == 0 and changes_since_sent > 0:
                stable_change_counter = stable_change_counter + 1
                # changes are stable
                if stable_change_counter > settings.compare_stable_frames:
                    print(f"Sending {changes_since_sent} changes")
                    cv2.imwrite(settings.last_sent_file, self.frames['sent_filtered'])
                    annotate(self.frames['annotated'], f"{changes_since_sent} changes.")
                    self.frames['sent_annotated']=self.frames['annotated']
                    return
                else:
                    annotate(self.frames['annotated'], f"{changes_since_sent} stable changes (waiting {stable_change_counter/settings.compare_stable_frames})")

            else:
                annotate(self.frames['annotated'], f"{current_changes} unstable changes.")
                stable_change_counter = 0

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        # we need at least one frame to start
        self.process_frame()

        while True:
            self.wait_for_stable_change()
            self.send()
