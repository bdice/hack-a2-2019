"""
WSGI config
"""

from citytours import CityTours, Tour

config = {
    'name': 'The Fairy Door',
}

tours_data = [{
    'name': 'birthday',
    'title': 'Birthday Deals',
    'data': 'tour_data/birthday_deals.csv',
}]

tours = {tour['name']: Tour(**tour) for tour in tours_data}

app = CityTours(config=config, tours=tours)
