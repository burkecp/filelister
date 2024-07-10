import os
from ctypes import c_wchar_p

import filelister as fs
import pytest

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "tmp_dir")


@pytest.fixture(scope="session")
def tmp_dir(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("data")
    flist_dir = tmp_path_factory.mktemp("filelists")
    for i in range(1, 6):
        with open(str(data_dir) + f"/sample_0{i}.txt", "w") as f:
            f.write("")
    with open(os.path.join(flist_dir, "bad_ext.png"), "w") as f:
        f.write("")
    return {"data": data_dir, "flists": flist_dir}


@pytest.fixture(scope="session")
def data_rel(tmp_dir):
    rel_data = [
        os.path.relpath(os.path.join(tmp_dir["data"], "sample_01.txt")),
        os.path.relpath(os.path.join(tmp_dir["data"], "sample_02.txt")),
        os.path.relpath(os.path.join(tmp_dir["data"], "sample_03.txt")),
        os.path.relpath(os.path.join(tmp_dir["data"], "sample_04.txt")),
        os.path.relpath(os.path.join(tmp_dir["data"], "sample_05.txt")),
    ]
    return [os.path.relpath(path) for path in rel_data]


@pytest.fixture(scope="session")
def data_abs(tmp_dir):
    return [
        os.path.abspath(os.path.join(tmp_dir["data"], "sample_01.txt")),
        os.path.abspath(os.path.join(tmp_dir["data"], "sample_02.txt")),
        os.path.abspath(os.path.join(tmp_dir["data"], "sample_03.txt")),
        os.path.abspath(os.path.join(tmp_dir["data"], "sample_04.txt")),
        os.path.abspath(os.path.join(tmp_dir["data"], "sample_05.txt")),
    ]


@pytest.fixture(scope="session")
def data_pfx(tmp_dir):
    return {
        "rel": os.path.relpath(tmp_dir["data"]),
        "abs": os.path.abspath(tmp_dir["data"]),
    }


@pytest.fixture(scope="session")
def data_no_ctx(tmp_dir):
    return ["sample_data_01.txt", "sample_data_02.txt", "sample_data_03.txt"]


test_data = [
    ("/home/christian/dir/filename_00.jpg", "./dir/filename_00.jpg"),
    ("/home/christian/dir/filename_01.jpg", "./dir/filename_01.jpg"),
    ("/home/christian/dir/filename_02.jpg", "./dir/filename_02.jpg"),
    ("/home/christian/dir/filename_03.jpg", "./dir/filename_03.jpg"),
    ("/home/christian/dir/filename_04.jpg", "./dir/filename_04.jpg"),
    ("/home/christian/dir/filename_05.jpg", "./dir/filename_05.jpg"),
]

abs_test_data = [item[0] for item in test_data]
rel_test_data = [item[1] for item in test_data]


def generator(data):
    for value in data:
        yield value[0], value[1]


def generator_new(abs, rel):
    for a, r in zip(abs, rel):
        yield a, r


def compare_color(value, color):
    if color == "red":
        start, stop = "\x1b[31m", "\x1b[0m\n"
        return value.startswith(start) and value.endswith(stop)


class TestDataStorage:
    def test_instantiation(self):
        storage = fs.DataStorage(generator(test_data))

    def test_initialize_paths(self):
        storage = fs.DataStorage(generator(test_data))
        assert isinstance(storage.paths, dict)
        for path in storage.paths["abs"] + storage.paths["rel"]:
            assert isinstance(path, str)

    def test_initialize_lookup(self):
        storage = fs.DataStorage(generator(test_data))
        assert isinstance(storage.lookup, dict)
        for entry in storage.lookup:
            assert isinstance(entry, str)
            assert isinstance(storage.lookup[entry], int)

    def test_initialize_curr_idx(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage.curr_idx == 0

    def test_len(self):
        storage = fs.DataStorage(generator(test_data))
        assert len(storage) == len(test_data)

    def test_disallow_duplicates(self, capsys):
        dupe_test_data = test_data * 2
        storage = fs.DataStorage(generator(dupe_test_data))
        assert len(storage) == len(test_data)

    def test_disallow_warning(self, capsys):
        dupe_test_data = test_data + [test_data[0]]
        storage = fs.DataStorage(generator(dupe_test_data))
        captured = capsys.readouterr()
        assert "WARN: Path is already stored. Skipping." in captured.out
        assert compare_color(str(captured.out), "red") == True

    def test_getitem_by_index(self):
        storage = fs.DataStorage(generator(test_data))
        for idx, test_item in enumerate(test_data):
            item = storage[idx]
            assert item[0] == test_item[0]
            assert item[1] == test_item[1]

    def test_getitem_by_slice_start(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[2:][0] == abs_test_data[2:]
        assert storage[2:][1] == rel_test_data[2:]
        assert storage[-2:][0] == abs_test_data[-2:]
        assert storage[-2:][1] == rel_test_data[-2:]

    def test_getitem_by_slice_start_stop(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[1:3][0] == abs_test_data[1:3]
        assert storage[1:3][1] == rel_test_data[1:3]
        assert storage[-1:3][0] == abs_test_data[-1:3]
        assert storage[-1:3][1] == rel_test_data[-1:3]
        assert storage[-3:-1][0] == abs_test_data[-3:-1]
        assert storage[-3:-1][1] == rel_test_data[-3:-1]

    def test_getitem_by_slice_start_stop_step(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[1:4:2][0] == abs_test_data[1:4:2]
        assert storage[1:4:2][1] == rel_test_data[1:4:2]
        assert storage[-1:4:2][0] == abs_test_data[-1:4:2]
        assert storage[-1:4:2][1] == rel_test_data[-1:4:2]
        assert storage[1:4:-2][0] == abs_test_data[1:4:-2]
        assert storage[1:4:-2][1] == rel_test_data[1:4:-2]
        assert storage[-1:-4:-2][0] == abs_test_data[-1:-4:-2]
        assert storage[-1:-4:-2][1] == rel_test_data[-1:-4:-2]

    def test_getitem_by_slice_stop(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[:2][0] == abs_test_data[:2]
        assert storage[:2][1] == rel_test_data[:2]
        assert storage[:-2][0] == abs_test_data[:-2]
        assert storage[:-2][1] == rel_test_data[:-2]

    def test_getitem_by_slice_stop_step(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[:4:2][0] == abs_test_data[:4:2]
        assert storage[:4:2][1] == rel_test_data[:4:2]
        assert storage[:4:-2][0] == abs_test_data[:4:-2]
        assert storage[:4:-2][1] == rel_test_data[:4:-2]

    def test_getitem_by_slice_step(self):
        storage = fs.DataStorage(generator(test_data))
        assert storage[::2][0] == abs_test_data[::2]
        assert storage[::2][1] == rel_test_data[::2]
        assert storage[::-2][0] == abs_test_data[::-2]
        assert storage[::-2][1] == rel_test_data[::-2]

    def test_getitem_throws_typeerror(self):
        storage = fs.DataStorage(generator(test_data))
        with pytest.raises(
            TypeError, match=r"indices must be integers or slices, not "
        ):
            storage["hello"]

    def test_contains(self):
        storage = fs.DataStorage(generator(test_data))
        for item in test_data:
            assert item[0] in storage
            assert item[1] in storage
        assert "hello" not in storage

    def test_iteration(self):
        storage = fs.DataStorage(generator(test_data))
        curr = 0
        for item in storage:
            assert item == test_data[curr]
            curr += 1

    def test_enumeration(self):
        storage = fs.DataStorage(generator(test_data))
        for idx, item in enumerate(storage):
            assert item == test_data[idx]

    def test_setitem(self, tmp_dir, data_abs, data_rel):
        storage = fs.DataStorage(generator(test_data))
        storage[0] = fs.Filelist([data_abs[0]])
        assert storage[0][0] == data_abs[0]
        assert storage[0][1] == data_rel[0]

    def test_setitem_slice(self, tmp_dir, data_abs, data_rel):
        storage = fs.DataStorage(generator_new(data_abs,data_rel))
        storage[0] = fs.Filelist(data_abs)
        assert storage[:][0] == data_abs
        assert storage[:][1] == data_rel
