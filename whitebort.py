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

        if self.sent_transform_frame is None:
            #ignore and store for next comparison
            self.sent_transform_frame=self.transform_frame
            self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame


    def wait_while_movement(self):
        """capture frames until there is no movement detected for while in self.transform_frame"""

        self.process_frame()
        last_frame = self.transform_frame
        last_time=time.time()

        while True:
            self.process_frame()

            change_count = compare.compare(last_frame, self.transform_frame)

            # no changes compared to last frame?
            if change_count == 0:
                no_change_time = int(time.time() - last_time)
                if no_change_time > settings.no_change_time:
                    print("Whiteboard is stable!".format(settings.no_change_time))
                    return
                else:
                    print("Board is stable for {} seconds. (waiting {}s)".format(no_change_time, settings.no_change_time))
            else:
                last_time=time.time()
                print("Waiting until board is stable: {} changes...".format(change_count))
            last_frame=self.transform_frame


    def compare_and_send(self):
        """compare transformed frame against last sent transformed frame. """
        change_count = compare.compare(self.transform_frame, self.sent_transform_frame)
        if change_count>0:
            print("Sending {} actual changes to telegram.".format(change_count))

            self.sent_transform_frame=self.transform_frame
            self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame

            #sent to telegram
            cv2.imwrite(settings.sent_transform_frame_file, self.sent_whiteboardenhance_frame)
            self.bot.send_message_image(settings.sent_transform_frame_file)
        else:
            print("No actual changes found.")


    def wait_until_movement(self):
        """"wait until there is movement detected"""
        self.process_frame()
        last_frame = self.transform_frame
        # last_time=time.time()

        while True:
            self.process_frame()

            change_count = compare.compare(last_frame, self.transform_frame)
            if change_count !=0:
                print("Movement detected, start processing.")
                return
            else:
                print("Waiting until there is movement...")


    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        while True:
            self.wait_while_movement()

            self.compare_and_send()

            self.wait_until_movement()

            # start_time=time.time()
            #
            # # print("Read...")
            # try:
            #
            #
            #     if prev_transform_frame is not None:
            #         # print("Compare...")
            #         change_count=compare.compare(prev_transform_frame, self.transform_frame, self.whiteboardenhance_frame)
            #
            #
            #         #no changes compared to last frame?
            #         if change_count==0:
            #             no_change_time=time.time() - last_change_time
            #             if no_change_time>settings.no_change_time:
            #
            #                 #check again last sent frame:
            #                 sent_change_count = compare.compare(sent_transform_frame, self.transform_frame,
            #                                                self.whiteboardenhance_frame)
            #                 #there are actual usefull changes compared to last sent:
            #                 if sent_change_count!=0:
            #                     print("Detected {} usefull changes. Sending...".format(sent_change_count))
            #
            #                     sent_transform_frame=self.transform_frame
            #
            #                     cv2.putText(self.whiteboardenhance_frame, "{} changes".format(sent_change_count), (10, 100),
            #                                 cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            #
            #                     self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame
            #                     cv2.imwrite("whiteboard.png", self.sent_whiteboardenhance_frame)
            #                     self.bot.send_message_image("whiteboard.png")
            #
            #             else:
            #                 print("No changes for {} seconds.".format(no_change_time))
            #
            #         else:
            #             last_change_time=time.time()
            #             print("Detected movement: {} changes".format(change_count))
            #
            #     prev_transform_frame=self.transform_frame
            #
            #     self.event.set()  # send signal to clients
            # except Exception as e:
            #     print(f"Error: {e}")
            #
            # # print("Sleep...")
            # time_left=settings.frame_time-(time.time()-start_time)
            # if time_left>0:
            #     time.sleep(time_left)

