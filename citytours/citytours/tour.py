import ast
import pandas as pd
from . import fetch_url
from .traveling_salesman import solve_tsp, get_directions, parse_latlngs

class Tour:
    def __init__(self, name, data, title, subtitle=None):
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.data = pd.read_csv(data)
        self.data = self.data.dropna(subset=['Address'])
        if 'latlng' not in self.data.columns:
            self.data['latlng'] = parse_latlngs(self.data.Address)
            self.data.to_csv(data)
        else:
            self.data['latlng'] = self.data['latlng'].apply(lambda x : ast.literal_eval(x))
        self.data = self.data.reset_index(drop=True)

    def __str__(self):
        return str(self.data)

    @property
    def fields(self):
        return list(self.data.columns)

    def generate_route(self, lat, lon):
        """Generate route from latitude and longitude."""
        data = self.data.head(8)  # Hard code number to use
        locations = data['Address'].tolist()
        locations = [[str(lat), str(lon)]] + locations
        location_order = solve_tsp(locations)
        indices = data.index.tolist()
        return [indices[i-1] for i in location_order if i != 0]
