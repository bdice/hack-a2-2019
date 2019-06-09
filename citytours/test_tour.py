from citytours.tour import Tour
import pandas as pd

if __name__ == "__main__":
    t = Tour('testtour', '../tour_data/birthday_deals.csv', 'title', 'subtitle')
    steps = t.generate_route(1, 1)
