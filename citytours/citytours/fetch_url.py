#!/usr/bin/env python3

from flask import Flask, url_for
app = Flask(__name__)
@app.route('https://www.google.com/maps/dir/?api=1&')
