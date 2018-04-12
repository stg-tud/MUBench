from data.misuse import Misuse


class FilterMisusesWithoutCorrectUsagesTask:
    def run(self, misuse: Misuse):
        if not misuse.correct_usages:
            raise UserWarning("Skipping {}: no correct usages.".format(misuse))
