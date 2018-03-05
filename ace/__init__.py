import os
from flask import Flask
from whitenoise import WhiteNoise

app = Flask(__name__)

# Use this app to serve static files.
wnapp = WhiteNoise(app, root='./ace/public/')