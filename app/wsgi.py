"""
WSGI config
"""

from citytours import CityTours

config = {
    'name': 'Ann Arbor City Tours',
}

app = CityTours(config=config)
