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


class Whitebort(object):

    def __init__(self, camera: Camera, bot: TelegramBot):

        self.camera = camera
        self.bot = bot
        self.thread = None  # background thread that reads frames from camera
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()
        self.compare= compare.Compare()

        self.frames:dict[str, Union[numpy.ndarray, None]] = {
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
            cv2.imwrite(telegram_file, self.frames['sent_whiteboardenhance_frame'])
            self.bot.send_message_image(telegram_file)

        a=self.frames['whiteboardenhance']


    def wait_for_stable_change(self):
        """process frames and wait until a change is stable
        """


        self.compare.clear()
        stable_change_counter=0

        while True:
            self.process_frame()
            now = time.time()

            if self.frames['sent_transform'] is None:
                self.frames['sent_transform'] = self.frames['transform']
                self.frames['sent_whiteboardenhance']=self.frames['whiteboardenhance']

            changes=self.compare.update(self.frames['sent_whiteboardenhance'], self.frames['whiteboardenhance'])
            self.compare.mark(self.frames['whiteboardenhance'])

            if changes==0 and self.compare.get_changes()>0:
                stable_change_counter=stable_change_counter+1
                if stable_change_counter>settings.compare_stable_frames:
                    return
            else:
                stable_change_counter=0

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        while True:
            self.wait_for_stable_change()
            self.send()
