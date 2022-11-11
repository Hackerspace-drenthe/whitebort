#!/usr/bin/env python
import cv2
from importlib import import_module
import os
from flask import Flask, render_template, Response

from camera_opencv import CameraOpenCV
from camera_transform import CameraTransform
from camera_whiteboardenhance import CameraWhiteboardEnhance

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        jpg=cv2.imencode('.jpg', frame)[1].tobytes() #TODO: move
        yield b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n--frame\r\n'


@app.route('/stream_input_stream')
def stream_input_stream():
    return Response(gen(input_stream),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_transformed')
def stream_transformed():
    return Response(gen(transformed),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/enhanced')
def stream_enhanced():
    return Response(gen(enhanced),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

input_stream=CameraOpenCV()
transformed=CameraTransform(input_stream)
enhanced=CameraWhiteboardEnhance(transformed)
app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
