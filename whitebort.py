import threading
import time

import settings
import transform
import whiteboardenhance
from camera import Camera
from clientevent import ClientEvent
import compare
import cv2

class Whitebort(object):

    def __init__(self, camera:Camera, frame_delay=0):

        self.camera=camera
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()
        self.frame_delay=frame_delay
        self.whiteboardenhance_frame=None
        self.sent_whiteboardenhance_frame=None

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

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        prev_transform_frame=None
        sent_transform_frame=None

        while True:
            start_time=time.time()

            # print("Read...")
            self.input_frame=self.camera.get_frame()

            if settings.save:
                cv2.imwrite(f"{int(time.time())}.png",self.input_frame)

            # print("Transform...")
            self.transform_frame=transform.transform(self.input_frame)
            if sent_transform_frame is None:
                sent_transform_frame=self.transform_frame

            # print("Enhance...")
            self.whiteboardenhance_frame = whiteboardenhance.whiteboard_enhance(self.transform_frame)
            if self.sent_whiteboardenhance_frame is None:
                self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame

            if prev_transform_frame is not None:
                # print("Compare...")
                change_count=compare.compare(prev_transform_frame, self.transform_frame, self.whiteboardenhance_frame)

                cv2.putText(self.whiteboardenhance_frame, "{} changes".format(change_count), (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

                #no changes compared to last frame?
                if change_count==0:

                    #check again last sent frame:
                    sent_change_count = compare.compare(sent_transform_frame, self.transform_frame,
                                                   self.whiteboardenhance_frame)
                    #there are actual usefull changes compared to last sent:
                    if sent_change_count!=0:
                        print("Detected {} usefull changes. Sending...".format(sent_change_count))

                        sent_transform_frame=self.transform_frame
                        self.sent_whiteboardenhance_frame=self.whiteboardenhance_frame
                    else:
                        print("No changes")

                else:
                    print("Detected movement: {} changes".format(change_count))

            prev_transform_frame=self.transform_frame

            self.event.set()  # send signal to clients

            # print("Sleep...")
            time_left=settings.frame_time-(time.time()-start_time)
            if time_left>0:
                time.sleep(time_left)

