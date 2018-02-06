class FilterList(list):
    def case_insensitive_contains(self, entry: str) -> bool:
        return any(e for e in self if e.lower() == entry.lower())
