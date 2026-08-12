


class BaseColumn:
    def __init__(self, consolidation_method):
        self.consolidation_method = consolidation_method


class GenderColumn(BaseColumn):
    def __init__(self):
        super().__init__(consolidation_method="single-select")


class RaceEthnicityColumn(BaseColumn):
    def __init__(self):
        super().__init__(consolidation_method="additive")


class DOBColumn(BaseColumn):
    def __init__(self):
        super().__init__(consolidation_method="single-select")


concept_classes = {
    "gender": GenderColumn(),
    "race/ethnicity": RaceEthnicityColumn(),
    "dob": DOBColumn(),
}