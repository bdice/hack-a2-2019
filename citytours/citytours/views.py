from flask import (session, redirect, request, url_for, send_file, flash,
                   abort, render_template, g, jsonify)
import json
import re
from .tour import Tour


def home(citytour):
    return redirect(url_for('tours_list'))


def tours_list(citytour):
    g.title = "Tours"
    g.subtitle = "get out | explore | adventure"
    g.tours = list(citytour.tours.values())
    return render_template('tours_list.html')


def show_tour(citytour, tourname):
    try:
        g.tour = citytour.tours[tourname]
        g.title = g.tour.title
        g.subtitle = g.tour.subtitle
        g.active_page = tourname
        return render_template('tour.html')
    except KeyError:
        abort(404, 'The tour requested could not be found.')

def get_tour_data(citytour, tourname):
    try:
        tour = citytour.tours[tourname]
        return jsonify(json.loads(tour.data.to_json(orient='records')))
    except KeyError:
        abort(404, 'The tour requested could not be found.')

def get_route_data(citytour, tourname):
    try:
        try:
            latlon =  request.form["user_location"]
        except:
            latlon = [42.278321, -83.746057]
        trip_order = citytour.tours[tourname].generate_route(*latlon)
        return jsonify(trip_order)
    except KeyError:
        abort(404, 'The tour requested could not be found.')


def get_file(citytour, tourid, filename):
    try:
        tour = citytour.project.open_tour(id=tourid)
    except KeyError:
        abort(404, 'The tour id requested could not be found.')
    else:
        if tour.isfile(filename):
            mimetype = None
            cache_timeout = 0
            # Return logs as plaintext
            textfile_regexes = ['tour-.*\\.[oe][0-9]*', '.*\\.log', '.*\\.dat']
            for regex in textfile_regexes:
                if re.match(regex, filename) is not None:
                    mimetype = 'text/plain'
            return send_file(tour.fn(filename), mimetype=mimetype,
                             cache_timeout=cache_timeout,
                             conditional=True)
        else:
            abort(404, 'The file requested does not exist.')


def settings(citytour):
    g.active_page = 'settings'
    return render_template('settings.html')


def page_not_found(citytour, error):
    return citytour._render_error(str(error))
