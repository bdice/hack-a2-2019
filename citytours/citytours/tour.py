import pandas as pd
from .traveling_salesman import solve_tsp, get_directions

class Tour:
    def __init__(self, name, data, title, subtitle=None):
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.data = pd.read_csv(data)

    def __str__(self):
        return str(self.data)

    @property
    def fields(self):
        return list(self.data.columns)

    def generate_route(self, lat, lon):
        """Generate route from latitude and longitude."""
        data = self.data.loc[~self.data['Address'].isna()]
        locations = data['Address']
        location_order = solve_tsp(locations)
        # Assuming just a numerical index.
        indices = data.index.tolist()
        data = data.reindex([indices[i] for i in location_order])
        sorted_locations = data['Address']
        legs = []
        for i in range(len(data)-1):
            steps = get_directions(sorted_locations.iloc[i], sorted_locations.iloc[i+1])
            legs.append(steps)

        self.legs = legs
