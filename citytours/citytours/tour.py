class Tour:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return str(self.data)

    @property
    def fields(self):
        return list(self.data.columns)

    @property
    def title(self):
        return self.title

    @property
    def subtitle(self):
        return self.subtitle
