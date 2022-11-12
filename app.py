#!/usr/bin/env python
import sys

#modified from https://github.com/miguelgrinberg/flask-video-streaming

import cv2
import os
from flask import Flask, render_template, Response
from _thread import get_ident




from whitebort import Whitebort

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/select.html')
def select():
    """Video streaming home page."""
    return render_template('select.html')


def stream_generator(frame_generator, nr):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = whitebort.get_frames()[nr]
        # print("Encode for client {}...".format(get_ident()))
        jpg=cv2.imencode('.jpg', frame)[1].tobytes() #TODO: move? (now its processed for every client)


        yield b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n--frame\r\n'


@app.route('/stream/<id>')
def stream(id):
    id=int(id)
    return Response(stream_generator(whitebort, id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if os.environ.get('CAMERA')=='pi':
    from camera_pi import CameraPi
    camera = CameraPi(frame_delay=1)
elif os.environ.get('CAMERA')=='opencv':
    from camera_opencv import CameraOpenCV
    camera = CameraOpenCV(frame_delay=1)
else:
    from camera_test import CameraTest
    camera = CameraTest()

if len(sys.argv)==2:
    print("Capturing frame to {}".format(sys.argv[1]))
    frame=camera.get_frame()
    cv2.imwrite(sys.argv[1], frame)
    sys.exit(0)

whitebort=Whitebort(camera)

# transformed=CameraTransform(input_stream)
# enhanced=CameraWhiteboardEnhance(transformed)
app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
