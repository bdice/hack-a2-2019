from flask import (session, redirect, request, url_for, send_file, flash,
                   abort, render_template, g)
import re


def home(citytour):
    return redirect(url_for('tours_list'))


def show_tour(citytour, tourid):
    try:
        tour = citytour.project.open_tour(id=tourid)
    except KeyError:
        abort(404, 'The tour id requested could not be found.')
    else:
        g.tours = citytour._get_tour_details([tour])
        g.title = g.tours[0]['title']
        g.subtitle = g.tours[0]['subtitle']
        return citytour._render_tour_view(default_view='grid')


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
