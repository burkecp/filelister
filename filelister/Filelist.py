"""
Class to handle Filelists
"""
import os
import zlib

from termcolor import colored

from .DataStorage import DataStorage


class Filelist:
    """
    Filelist class for creating, manipulating, comparing, and exporting filelists.
    """

    def __init__(self, input_data, accepted_exts=None):
        self._state = None  # abs, rel, or na
        self._prefixes = {"abs": "", "rel": "", "curr": ""}
        self._data_storage = None
        if accepted_exts is None:
            accepted_exts = False

        # get location of caller
        # self._caller_loc = os.path.dirname(
        #    inspect.currentframe().f_back.f_globals["__file__"]
        # )

        if isinstance(input_data, Filelist):
            raise TypeError(colored(f"{input_data} is already a Filelist", "red"))

        if not isinstance(input_data, (list, set, tuple, str)):  # add iterables
            raise TypeError(colored(f"Invalid input type: {type(input_data)}", "red"))

        if isinstance(input_data, (list, set, tuple)):
            self._build_internal(list(input_data), accepted_exts)

        if isinstance(input_data, str):
            try:
                if not os.path.isdir(input_data):
                    raise FileNotFoundError(
                        colored(f"{input_data} is not a directory", "red")
                    )
                tmp = []
                for path, _, files in os.walk(input_data):
                    for filename in files:
                        tmp.append(path + os.sep + filename)
                self._build_internal(tmp, accepted_exts)
            except Exception as e:
                raise e

    def _build_internal(self, input_data, accepted_exts):
        self._prefixes["curr"] = os.path.dirname(os.path.commonprefix(input_data))

        if self._prefixes["curr"].startswith(os.sep):
            self._state = "abs"
        elif self._prefixes["curr"] == "":
            self._state = "na"
        else:
            self._state = "rel"

        self._prefixes["abs"] = os.path.abspath(self._prefixes["curr"])
        self._prefixes["rel"] = (
            os.path.relpath(self._prefixes["curr"], start=os.getcwd())
            if not self.is_na()
            else ""
        )
        self._data_storage = DataStorage(self._loader(input_data, accepted_exts))

    def _loader(self, input_data, accepted_exts):
        for value in input_data:
            if accepted_exts:
                if os.path.splitext(value)[1] in accepted_exts:
                    yield self._get_abs_path(value), self._get_rel_path(value)
                else:
                    print(colored(f"Invalid exception found. Skipping {value}.", "red"))
            else:
                yield self._get_abs_path(value), self._get_rel_path(value)

    def _get_abs_path(self, path):
        unique_path = path[len(self._prefixes["curr"]) :]
        if not unique_path.startswith("/"):
            unique_path = "/" + unique_path

        return self._prefixes["abs"] + unique_path

    def _get_rel_path(self, path):
        unique_path = path[len(self._prefixes["curr"]) :]
        if self._state == "na" and self._prefixes["rel"] != "":
            unique_path = "/" + unique_path
        return self._prefixes["rel"] + unique_path

    def to_list(self):
        """Returns the Filelist as a List"""
        if self.is_abs():
            return self._data_storage.paths["abs"]
        return self._data_storage.paths["rel"]

    def _to_abs_list(self):
        return self._data_storage.paths["abs"]

    def _to_rel_list(self):
        return self._data_storage.paths["rel"]

    def __iter__(self):
        return iter(self.to_list())

    def __len__(self):
        return len(self._data_storage)

    def __getitem__(self, idx):
        if isinstance(idx, (int, slice)):
            return (
                self._data_storage[idx][0]
                if self.is_abs()
                else self._data_storage[idx][1]
            )
        raise TypeError(
            colored(f"indices must be integers or slices, not {type(idx)}", "red")
        )

    def __setitem__(self, idx, value):
        if isinstance(idx, slice):
            try:
                if len(value) != len(range(*idx.indices(len(value)))):
                    raise ValueError
                fl = Filelist(value)
            except ValueError:
                raise ValueError(
                    colored("Input must be the same length as the slice", "red")
                )
            except Exception as e:
                raise TypeError(colored("Invalid input for filelist", "red"))
        else:
            if not isinstance(value, str):
                raise TypeError(
                    colored(
                        f"Invalid input: filename must be a string, not {type(value)}",
                        "red",
                    )
                )
            fl = Filelist([value])

        self._data_storage[idx] = fl

    def __contains__(self, filename):
        if not isinstance(filename, str):
            raise TypeError(colored("Invalid input: filename must be a string", "red"))
        return filename in self._data_storage

    def __str__(self):
        if self._data_storage:
            str_out = ""
            for fname in self.to_list():
                str_out += "\n" + fname
            return colored(str_out, "cyan")
        return colored("Empty Filelist", "red")

    def __repr__(self):
        idx = 0 if self.is_abs() else 1
        if len(self._data_storage) > 10:
            return colored(
                f"Filelist({self._data_storage[:5][idx], ..., self._data_storage[:-5][idx]})",
                "cyan",
            )
        return colored(f"Filelist({str(self._data_storage[:][idx])})", "cyan")

    def is_abs(self):
        """Returns true if storing an absolute Filelist and false otherwise."""
        return self._state == "abs"

    def is_rel(self):
        """Returns true if storing a relative Filelist and false otherwise."""
        return self._state == "rel"

    def is_na(self):
        """Returns true if storing a NA Filelist and false otherwise."""
        return self._state == "na"

    def to_abs(self):
        """Converts the existing Filelist to an absolute Filelist."""
        if not self.is_abs():
            self._prefixes["curr"] = self._prefixes["abs"]
            self._state = "abs"
        return self

    def to_rel(self):
        """Converts the existing Filelist to a relative Filelist."""
        if not self.is_rel():
            self._prefixes["curr"] = self._prefixes["rel"]
            self._state = "rel"
        return self

    def contains(self, filename):
        """
        Returns True if the filelist contains a given filename.
        """
        if not isinstance(filename, str):
            raise TypeError(colored("Invalid input: filename must be a string", "red"))
        return filename in self._data_storage

    def save(self, outfile="filelist.txt", output_type=None, compressed=False):
        """
        Saves a Filelist.
        Args:
            outfile (str, optional): path and filename to output filelist
            output_type (str, optional): whether to save a relative, absolute, or na filelist
            compressed(bool, optional): whether or not to compress the output filelist
                abs: save outpaths as abspaths
                rel: save outpaths as relpaths, relative to outfile
                na: saves only the filenames
        """
        if not isinstance(outfile, str):
            raise TypeError(
                colored(f"Output file must be str, not {type(outfile)}", "red")
            )
        if not os.path.isdir(os.path.dirname(os.path.abspath(outfile))):
            raise ValueError(colored("Output directory does not exist", "red"))

        if output_type is None:
            output_type = self._state

        out_data = self._normalize_paths(output_type, outfile)

        if compressed:
            with open(outfile, "wb") as f:
                f.write(self._compress(out_data))
        else:
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(os.linesep.join(out_data))

    def _normalize_paths(self, target_type, target_file):
        """
        target_type: type of Filelist to write
        target_file: path to desired Filelist location
        """
        if target_type == "abs":
            return self._to_abs_list()
        if target_type == "rel":
            target_prefix = os.path.relpath(
                self._prefixes["curr"], start=os.path.dirname(target_file)
            )
            return [
                target_prefix + path[len(self._prefixes["rel"]) :]
                for path in self._to_rel_list()
            ]
        if target_type == "na":
            if self._state == "na":
                return self.to_list()
            return [path[len(self._prefixes["curr"]) + 1 :] for path in self.to_list()]
        raise TypeError(colored("Desired target type is unknown", "red"))

    def _compress(self, data):
        zdict = self._prefixes["curr"].encode("utf-8")
        obj = zlib.compressobj(level=1, memLevel=9, zdict=zdict)
        data = ",".join(data).encode("utf-8")
        data_zip = obj.compress(data)
        data_zip += obj.flush()
        data_zip = zdict + b"\n" + data_zip
        return data_zip
