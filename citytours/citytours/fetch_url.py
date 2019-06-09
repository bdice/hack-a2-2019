from flask import Flask, url_for
app = Flask(__name__)

# Generates url with all destinations
@app.route('/https://www.google.com/maps/dir/')
def google_maps(): pass

def fetch_url(coord,
              travelmode='walking'):
    origin = '%f,%f' % (coord[0][0], coord[0][1])
    destination = '%f,%f' % (coord[-1][0], coord[-1][1])
    with app.test_request_context():
        if len(coord) == 2:
            map_url = url_for('google_maps',
                                api=1,
                                origin=origin,
                                destination=destination,
                                travelmode=travelmode)
            return map_url
        if len(coord) > 2:
            waypoint = None
            for n in range(1,(len(coord)-1)):
                if waypoint is None:
                    waypoint = '%f,%f' % (coord[n][0], coord[n][1])
                else:
                    waypoint += '|%f,%f' % (coord[n][0], coord[n][1])

            map_url = url_for('google_maps',
                              api=1,
                              origin=origin,
                              destination=destination,
                              travelmode=travelmode,
                              waypoints=waypoint)
            return map_url
