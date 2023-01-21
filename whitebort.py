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

    def __init__(self, camera:Camera, bot: TelegramBot):

        self.camera=camera
        self.bot=bot
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()

        self.input_frame=None                   # raw input frame from cam
        self.transform_frame=None               # transformed frame (cropping, skew, rotate, mirror etc)
        self.whiteboardenhance_frame=None       # transformed AND enchanged with whiteboard filter

        self.sent_whiteboardenhance_frame=None  # last sent frames to telegram
        self.sent_transform_frame=None

        if os.path.isfile(settings.sent_transform_frame_file):
            self.sent_transform_frame=cv2.imread(settings.sent_transform_frame_file)
        else:
            print("ERROR: {} not found!".format(settings.sent_transform_frame_file))

        """Start the background camera thread if it isn't running yet."""
        self.last_access = time.time()

        # start background frame thread
        self.thread = threading.Thread(target=self._thread)
        self.thread.start()

        self.input_frame=[]

    def get_frames(self, wait=True):
        """Wait until a frame is processed and get all in-between processing steps"""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        if wait:
            self.event.wait()
            self.event.clear()

        return [self.input_frame, self.transform_frame, self.whiteboardenhance_frame, self.sent_whiteboardenhance_frame]


    def process_frame(self):
        """get next frame, do processing and store in self"""
        self.input_frame = self.camera.get_frame()

        if settings.save:
            cv2.imwrite(f"{int(time.time())}.png", self.input_frame)

        self.transform_frame = transform.transform(self.input_frame)
        self.whiteboardenhance_frame = whiteboardenhance.whiteboard_enhance(self.transform_frame)





    def compare_and_send(self):
        """compare transformed frame against last sent transformed frame. """

        if self.sent_transform_frame is None:
            #ignore and store for next comparison
            self.sent_transform_frame=self.transform_frame
            self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame
            print("(Ignoring first changes)")
            return

        change_count = compare.compare(self.transform_frame, self.sent_transform_frame, self.whiteboardenhance_frame)
        if change_count>0:
            print("Sending {} actual changes to telegram.".format(change_count))
            cv2.putText(self.whiteboardenhance_frame, "{} changes".format(change_count), (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

            self.sent_transform_frame=self.transform_frame
            self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame

            #store for future comparison after program restart
            cv2.imwrite(settings.sent_transform_frame_file, self.sent_transform_frame)

            #sent to telegram
            telegram_file="telegram.png"
            cv2.imwrite(telegram_file, self.sent_whiteboardenhance_frame)
            self.bot.send_message_image(telegram_file)
        else:
            print("No actual changes found.")



    def wait_for_stable_change(self):
        """process frames and wait until a change is stable

        e.g.: change compared to previous sent_transform_frame is stable AND no changes to last_frame is stable.
        for a while.

        """

        self.process_frame()
        last_frame = self.transform_frame
        last_change_time=time.time()
        last_sent_change_count=0

        while True:
            self.process_frame()
            now=time.time()

            # changes compared to last frame?
            change_count = compare.compare(self.transform_frame, last_frame, self.whiteboardenhance_frame)
            if change_count:
                print("Movement detected: {} changes.".format(change_count))
                last_change_time=now

            # no changes to last sent frame? or number of changes has changed?
            change_count = compare.compare(self.transform_frame, self.sent_transform_frame)
            if change_count==0 or change_count!=last_sent_change_count:
                if change_count!=last_sent_change_count:
                    print("Unstable changes: {} (was {})".format(change_count, last_sent_change_count))
                elif change_count==0:
                    print("No changes")

                last_change_time=now
                last_sent_change_count=change_count

            no_change_time = int(now - last_change_time)
            if no_change_time > settings.no_change_time:
                print("Stable change detected!".format(settings.no_change_time))
                return
            else:
                if no_change_time>0:
                    print("Board has {} stable changes for {} seconds. (waiting {}s)".format(change_count, no_change_time, settings.no_change_time))

            last_frame = self.transform_frame

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        while True:
            self.wait_for_stable_change()
            self.compare_and_send()


