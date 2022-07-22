import os

import filelister as fs
import pytest


def rel_to_abs(path):
    return os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(__file__), path))


sample_data = ["data/sample_01.txt", "data/sample_02.txt", "data/sample_03.txt"]
sample_data = [rel_to_abs(path) for path in sample_data]
sample_data2 = ["data/sample_03.txt", "data/sample_04.txt", "data/sample_05.txt"]
sample_data2 = [rel_to_abs(path) for path in sample_data2]
rel_sample = [os.path.relpath(path, start=os.getcwd()) for path in sample_data]
rel_sample2 = [os.path.relpath(path, start=os.getcwd()) for path in sample_data2]

test_data2 = [os.path.abspath(test) for test in sample_data2]
test_data = [os.path.abspath(test) for test in sample_data]
test_set = set(test_data).union(set(test_data2))
test_list = test_data + test_data2[1:]


class CreateFromType:
    def test_filelist_create_from_abs_list(self):
        flist = fs.Filelist(sample_data)
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_rel_list(self):
        flist = fs.Filelist(rel_sample)
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_bad_list(self):
        test = "test_file"
        test_list = sample_data.copy()
        test_list.append(test)
        flist = fs.Filelist(test_list)
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_abs_set(self):
        flist = fs.Filelist(set(test_data))
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_rel_set(self):
        flist = fs.Filelist(set(rel_sample))
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_dir(self):
        flist = fs.Filelist(rel_to_abs("data"))
        assert set(flist.data) == set(test_data).union(set(test_data2))

    def test_filelist_create_from_abs_tuple(self):
        flist = fs.Filelist(tuple(sample_data))
        assert set(flist.data) == set(test_data)

    def test_filelist_create_from_rel_tuple(self):
        flist = fs.Filelist(tuple(rel_sample))
        assert set(flist.data) == set(test_data)


class TestUtils:
    def test_save_abs(self):
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/test_filelist_abs.txt"
        )
        flist = fs.Filelist(sample_data)
        flist.save(test_path)
        with open(test_path, encoding="utf-8") as f:
            saved_data = [line.rstrip() for line in f]
            assert saved_data == test_data

    def test_save_rel(self):
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/test_filelist_rel.txt"
        )
        flist = fs.Filelist(sample_data)
        flist.save(test_path, relative=True)
        with open(test_path, encoding="utf-8") as f:
            saved_data = [
                os.path.normpath(
                    os.path.join(os.path.dirname(test_path), line.rstrip())
                )
                for line in f
            ]
            assert saved_data == test_data

    def test_read_filelist_abs(self):
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/test_filelist_abs.txt"
        )
        flist = fs.read_filelist(test_path)
        assert flist.data == test_data

    def test_read_filelist_rel(self):
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/test_filelist_rel.txt"
        )
        flist = fs.read_filelist(test_path)
        assert flist.data == test_data

    def test_contains_abs(self):
        flist = fs.Filelist(test_set)
        assert flist.contains(sample_data[0]) is True

    def test_not_contains_abs(self):
        flist = fs.Filelist(test_set)
        assert flist.contains("/not_a_file") is False

    def test_contains_rel(self):
        flist = fs.Filelist(test_set)
        assert flist.contains(rel_sample[0]) is True

    def test_not_contains_rel(self):
        flist = fs.Filelist(test_set)
        assert flist.contains("not_a_file") is False

    def test_contains_throws_typeerror(self):
        flist = fs.Filelist(test_set)
        with pytest.raises(TypeError, match="Invalid input: filename must be a string"):
            flist.contains(1234)

    def test_write_filelist(self):
        fs.write_filelist(
            os.path.join(os.getcwd(), os.path.dirname(__file__), "data"),
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                "filelists/write_filelist_t.txt",
            ),
        )
        flist = fs.read_filelist(
            os.path.join(
                os.getcwd(), os.path.dirname(__file__), "filelists/write_filelist_t.txt"
            )
        )
        assert set(flist.data) == test_set


class TestCompression:
    """
    tests for reading and writing compressed filelists
    """

    def test_save_abs_compressed(self):
        """
        tests ability to save a compressed absolute filelist
        """
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/compressed_abs.txt"
        )
        flist = fs.Filelist(sample_data)
        flist.save(test_path, relative=False, compressed=True)
        compressed_size = os.stat(test_path).st_size
        uncompressed_size = os.stat(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                "filelists/test_filelist_abs.txt",
            )
        ).st_size
        assert compressed_size < uncompressed_size

    def test_read_abs_compressed(self):
        """
        tests ability to read compressed absolute filelist
        """
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/compressed_abs.txt"
        )
        flist = fs.read_filelist(test_path, check_exists=True, compressed=True)
        assert flist.data == test_data

    def test_save_rel_compressed(self):
        """
        tests ability to save a compressed absolute filelist
        """
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/compressed_rel.txt"
        )
        flist = fs.Filelist(test_set)
        flist.save(test_path, relative=True, compressed=True)
        compressed_size = os.stat(test_path).st_size
        uncompressed_size = os.stat(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                "filelists/full_filelist_rel.txt",
            )
        ).st_size
        assert compressed_size < uncompressed_size

    def test_read_rel_compressed(self):
        """
        tests ability to read compressed absolute filelist
        """
        test_path = os.path.join(
            os.getcwd(), os.path.dirname(__file__), "filelists/compressed_rel.txt"
        )
        flist = fs.read_filelist(test_path, check_exists=True, compressed=True)
        print(flist.data)
        assert set(flist.data) == test_set
