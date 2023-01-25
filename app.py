#!/usr/bin/env python
import argparse
import sys
import time

import settings

#modified from https://github.com/miguelgrinberg/flask-video-streaming

import cv2
import os
from flask import Flask, render_template, Response
from _thread import get_ident

import telegram_bot
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


def stream_generator(frame_generator, id):
    """Video streaming generator function."""

    def send(wait):
        frame = whitebort.get_frames(wait=wait)[id]
        jpg=cv2.imencode('.jpg', frame)[1].tobytes() #TODO: move? (now its processed for every client)
        yield b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n--frame\r\n'

    yield b'--frame\r\n'

    #buffer..
    yield from send(wait=False)
    yield from send(wait=False)
    yield from send(wait=False)

    while True:
        yield from send(wait=True)


@app.route('/stream/<id>')
def stream(id):
    return Response(stream_generator(whitebort, id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



if settings.mode=='pi':
    from camera_pi import CameraPi
    camera = CameraPi()
elif settings.mode=='opencv':
    from camera_opencv import CameraOpenCV
    camera = CameraOpenCV()
elif settings.mode == 'url':
    from camera_url import CameraURL
    camera = CameraURL(settings.url)
elif settings.mode=='test':
    from camera_test import CameraTest
    camera = CameraTest()

if len(sys.argv)==2:
    print("Capturing frame to {}".format(sys.argv[1]))
    frame=camera.get_frame()
    cv2.imwrite(sys.argv[1], frame)
    sys.exit(0)

# telegram_bot=telegram_bot.TelegramBot()
telegram_bot=None

whitebort=Whitebort(camera, telegram_bot)

# transformed=CameraTransform(input_stream)
# enhanced=CameraWhiteboardEnhance(transformed)
app.run(host='0.0.0.0', threaded=True, debug=True, use_reloader=False)
