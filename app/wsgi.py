"""
WSGI config
"""

from citytours import CityTours

config = {
    'name': 'Ann Arbor City Tours',
}

tours = [{
    'name': 'birthday',
    'title': 'Birthday Deals',
    'data': 'tours/birthday_deals.csv',
}]

app = CityTours(config=config, tours=tours)
