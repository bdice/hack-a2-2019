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

    def __str__(self):
        return str(self.data)

    @property
    def fields(self):
        return list(self.data.columns)

    def generate_route(self, lat, lon):
        """Generate route from latitude and longitude."""
        data = self.data.loc[~self.data['Address'].isna()]
        locations = data['Address'].tolist()
        locations.append([str(lat), str(lon)])
        max_index = len(locations)-1
        location_order = solve_tsp(locations, max_index)
        # Assuming just a numerical index.
        indices = data.index.tolist()
        data = data.reindex([indices[i] for i in location_order if i != max_index])
        sorted_locations = data['Address']
        legs = []
        for i in range(len(data)-1):
            steps = get_directions(sorted_locations.iloc[i], sorted_locations.iloc[i+1])
            legs.append(steps)

        self.legs = legs
        return legs
