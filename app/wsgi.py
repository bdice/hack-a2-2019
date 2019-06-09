"""
WSGI config
"""

from citytours import CityTours

config = {
    'name': 'Ann Arbor City Tours',
}

tours = {
    'birthday': 'tours/birthday_deals.csv'
}

app = CityTours(config=config, tours=tours)
