"""DataStorage class"""
from termcolor import colored


class DataStorage:
    """Class to store Filelist data"""

    def __init__(self, loader):
        self.paths = {"abs": [], "rel": []}
        self.lookup = {}
        self.counter = 0
        self.curr_idx = 0

        for abs_path, rel_path in loader:
            if abs_path in self.lookup or rel_path in self.lookup:
                print(colored("WARN: Path is already stored. Skipping.", "red"))
                continue

            self.paths["abs"].append(abs_path)
            self.paths["rel"].append(rel_path)

            self.lookup[abs_path] = self.counter
            self.lookup[rel_path] = self.counter

            self.counter += 1

        assert self.counter == len(self.paths["abs"]) == len(self.paths["rel"])

    def __len__(self):
        return self.counter

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.paths["abs"][key], self.paths["rel"][key]

        if isinstance(key, slice):
            start, stop, step = key.indices(self.counter)
            ret_abs = []
            ret_rel = []
            for idx in range(start, stop, step):
                abs_path, rel_path = self.paths["abs"][idx], self.paths["rel"][idx]
                ret_abs.append(abs_path)
                ret_rel.append(rel_path)
            return ret_abs, ret_rel
        raise TypeError(f"indices must be integers or slices, not {type(key)}")

    def __setitem__(self, key, value):

        self.paths["abs"][key] = value.to_abs()[key]
        self.paths["rel"][key] = value.to_rel()[key]

    def __contains__(self, value):
        return value in self.lookup

    def __iter__(self):
        self.curr_idx = 0
        return self

    def __next__(self):
        if self.curr_idx < self.counter:
            result = self[self.curr_idx]
            self.curr_idx += 1
            return result
        raise StopIteration

    def index(self, value):
        """Returns the index of value in DataStorage"""
        if value in self.lookup:
            return self.lookup[value][1]
        raise ValueError(f"{value} is not in DataStorage")

    def count(self, value):
        """Returns the number of occurrences of value in DataStorage"""
        return 1 if value in self.lookup else 0
