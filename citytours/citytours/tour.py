class Tour:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    @property
    def fields(self):
        return list(self.data.columns)
