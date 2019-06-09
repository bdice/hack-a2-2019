import googlemaps
from datetime import datetime
import bs4


API_KEY = 'YOUR_API_KEY'


def get_directions(origin, destination, mode="driving", waypoints=None):
    """Get directions between two locations.

    Args:
        origin (str): An origin in a format acceptable to the Google Maps API.
        destination (str): A destination in a format acceptable to the Google
                            Maps API.

    Returns:
        list: A list of strings with directions.
    """
    gmaps = googlemaps.Client(key=API_KEY)

    # Request directions via public transit
    now = datetime.now()
    result = gmaps.directions(origin,
                              destination,
                              mode=mode,
                              waypoints=waypoints,
                              departure_time=now)

    legs = result[0]['legs'][0]
    steps = legs['steps']
    directions = []
    for step in steps:
        soup = bs4.BeautifulSoup(step['html_instructions'], features='html.parser')
        directions.append(soup.get_text())

    return directions


def get_distance_matrix(origins, destinations):
    """Get distance matrix between pairs of origins and destinations.

    Args:
        origins (list): List of origins in a format acceptable to the Google
                        Maps API.
        destinations (list): List of destinations in a format acceptable to the
                             Google Maps API.

    Returns:
        list: A 2D list of distances.
    """
    gmaps = googlemaps.Client(key=API_KEY)

    # Request directions via public transit
    result = gmaps.distance_matrix(origins, destinations)

    # Construct distance matrix from result
    matrix = []
    for row in result['rows']:
        mat_row = []
        for element in row['elements']:
            # The value is in meters
            mat_row.append(element['distance']['value'])
        matrix.append(mat_row)

    return matrix
