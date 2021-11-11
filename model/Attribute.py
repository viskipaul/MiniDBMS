class Attribute:
    def __init__(self, name, type, pk, is_null = True, length = 1):
        self.name = name
        self.pk = pk
        self.is_null = is_null
        self.length = length
        self.type = type