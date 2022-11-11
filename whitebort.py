import threading
import time

import transform
import whiteboardenhance
from camera import Camera
from clientevent import ClientEvent


class Whitebort(object):

    def __init__(self, camera:Camera, frame_delay=0):

        self.camera=camera
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.event = ClientEvent()
        self.frame_delay=frame_delay

        """Start the background camera thread if it isn't running yet."""
        self.last_access = time.time()

        # start background frame thread
        self.thread = threading.Thread(target=self._thread)
        self.thread.start()

        self.input_frame=[]

    def get_frames(self):
        """Wait until a frame is processed and get all in-between processing steps"""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return [self.input_frame, self.transform_frame, self.whiteboardenhance_frame]

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')

        while True:
            print("Read...")
            self.input_frame=self.camera.get_frame()
            print("Transform...")
            self.transform_frame=transform.transform(self.input_frame)
            print("Enhance...")
            self.whiteboardenhance_frame=whiteboardenhance.whiteboard_enhance(self.transform_frame)

            self.event.set()  # send signal to clients
            time.sleep(0)

