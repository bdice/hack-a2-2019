#!/usr/bin/env python3

from flask import Flask, url_for
app = Flask(__name__)

# Generates url with all destinations
@app.route('/https://www.google.com/maps/dir/')
def overview(): pass

# Generates url with directions from one point to another on the map
@app.route('/https://www.google.com/maps/dir/')
def direct(): pass

with app.test_request_context():
    overview_url = url_for('overview',
                           api=1,
                           origin='42.285416, -83.746748',
                           destination='42.287437, -83.734708',
                           travelmode='walking',
                           waypoints='42.296798, -83.713075 | 42.285416, -83.746748')
    direct_url = url_for('direct',
                         api=1,
                         origin='42.285416, -83.746748',
                         destination='42.287437, -83.734708',
                         travelmode='walking')

