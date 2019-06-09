import pandas as pd

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
