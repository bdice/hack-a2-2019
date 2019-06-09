import pandas as pd
from .tour import Tour

def parse_tour(path):
    return Tour(pd.read_csv(path))
