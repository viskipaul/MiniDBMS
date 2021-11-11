class ForeignKey:
    def __init__(self, attribute, ref_table, ref_attribute):
        self.attribute = attribute
        self.ref_table = ref_table
        self.ref_attribute = ref_attribute