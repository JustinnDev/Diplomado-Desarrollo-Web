
class MaterialType:
    def __init__(self, id=None, name=None, category=None, base_price=None):
        self.id = id
        self.name = name
        self.category = category
        self.base_price = base_price

class MaterialReception:
    def __init__(self, id=None, client=None, reception_date=None, notes=None):
        self.id = id
        self.client = client
        self.reception_date = reception_date
        self.notes = notes