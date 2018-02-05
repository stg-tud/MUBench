from data.misuse import Misuse


class FilterMisusesWithoutPatternsTask:
    def run(self, misuse: Misuse):
        if not misuse.patterns:
            raise UserWarning("Skipping {}: no patterns.".format(misuse))
