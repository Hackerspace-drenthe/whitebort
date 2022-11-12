from io import BytesIO

import cv2

from camera_pi import CameraPi
from flask import Flask, render_template, Response
import flask



#simple snapshot server for raspi cam

camera=CameraPi()
app = Flask(__name__)
@app.route('/')
def index():
    frame=camera.get_frame()
    encoded=cv2.imencode('.png', frame)[1].tobytes()
    return flask.send_file(BytesIO(encoded), 'image/png')


app.run(host='0.0.0.0', threaded=False, debug=True, use_reloader=False)



