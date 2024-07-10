"""Tests for Filelist"""
import os
from pathlib import Path

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


class TestCreateFromType:
    def test_filelist_create_from_abs_list(self, tmp_dir, data_abs, data_pfx):
        flist = fs.Filelist(data_abs)
        assert flist.to_list() == data_abs
        assert flist._prefixes["curr"] == data_pfx["abs"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_rel_list(self, tmp_dir, data_rel, data_pfx):
        flist = fs.Filelist(data_rel)
        assert flist.to_list() == data_rel
        assert flist._prefixes["curr"] == data_pfx["rel"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_abs_set(self, tmp_dir, data_abs, data_pfx):
        flist = fs.Filelist(set(data_abs))
        assert set(flist.to_list()) == set(data_abs)
        assert flist._prefixes["curr"] == data_pfx["abs"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_rel_set(self, tmp_dir, data_rel, data_pfx):
        flist = fs.Filelist(set(data_rel))
        assert set(flist.to_list()) == set(data_rel)
        assert flist._prefixes["curr"] == data_pfx["rel"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_abs_dir(self, tmp_dir, data_abs, data_pfx):
        flist = fs.Filelist(os.path.abspath(tmp_dir["data"]))
        assert set(flist.to_list()) == set(data_abs)
        assert flist._prefixes["curr"] == data_pfx["abs"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_rel_dir(self, tmp_dir, data_rel, data_pfx):
        flist = fs.Filelist(os.path.relpath(tmp_dir["data"]))
        assert set(flist.to_list()) == set(data_rel)
        assert flist._prefixes["curr"] == data_pfx["rel"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_abs_tuple(self, tmp_dir, data_abs, data_pfx):
        flist = fs.Filelist(tuple(data_abs))
        assert flist.to_list() == data_abs
        assert flist._prefixes["curr"] == data_pfx["abs"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_filelist_create_from_rel_tuple(self, tmp_dir, data_rel, data_pfx):
        flist = fs.Filelist(tuple(data_rel))
        assert flist.to_list() == data_rel
        assert flist._prefixes["curr"] == data_pfx["rel"]
        assert flist._prefixes["abs"] == data_pfx["abs"]
        assert flist._prefixes["rel"] == data_pfx["rel"]

    def test_create_with_no_context(self, tmp_dir, data_no_ctx):
        flist = fs.Filelist(data_no_ctx)
        assert flist.to_list() == [os.path.relpath(fname) for fname in data_no_ctx]
        assert flist._prefixes["curr"] == ""
        assert flist._prefixes["abs"] == os.path.abspath(".")
        assert flist._prefixes["rel"] == ""

    def test_remove_bad_exts(self, tmp_dir, data_no_ctx):
        test_data = data_no_ctx + ["bad_file.png", "worse_file.tiff", "good_file.jpg"]
        flist = fs.Filelist(test_data, [".txt", ".jpg"])
        assert flist.to_list() == data_no_ctx + ["good_file.jpg"]


class TestConversions:
    def test_abs_to_rel(self, tmp_dir, data_abs, data_rel, data_pfx):
        flist = fs.Filelist(data_abs)
        rel_flist = flist.to_rel()
        assert rel_flist.to_list() == data_rel
        assert rel_flist._prefixes["curr"] == data_pfx["rel"]

    def test_rel_to_abs(self, tmp_dir, data_abs, data_rel, data_pfx):
        flist = fs.Filelist(data_rel)
        rel_flist = flist.to_abs()
        assert rel_flist.to_list() == data_abs
        assert rel_flist._prefixes["curr"] == data_pfx["abs"]

    def test_abs_to_abs_returns_self(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist.to_abs() is flist

    def test_rel_to_rel_returns_self(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        assert flist.to_rel() is flist

    def test_no_context_to_abs(self, tmp_dir, data_no_ctx):
        flist = fs.Filelist(data_no_ctx)
        abs_flist = flist.to_abs()
        assert abs_flist.to_list() == [os.path.abspath(fname) for fname in data_no_ctx]


class TestUtils:
    def test_save_abs(self, tmp_dir, data_abs):
        test_path = os.path.join(tmp_dir["flists"], "abs_filelist.txt")
        flist = fs.Filelist(data_abs)
        flist.save(test_path)
        with open(test_path, encoding="utf-8") as f:
            saved_data = [line.rstrip() for line in f]
            assert saved_data == data_abs

    def test_save_rel(self, tmp_dir, data_rel):
        test_path = os.path.join(tmp_dir["flists"], "rel_filelist.txt")
        flist = fs.Filelist(data_rel)
        flist.save(test_path)
        with open(test_path, encoding="utf-8") as f:
            saved_data = [
                os.path.relpath(os.path.join(tmp_dir["flists"], line.rstrip()))
                for line in f
            ]
            assert saved_data == data_rel

    def test_read_filelist_abs(self, tmp_dir, data_abs):  # depends on test_save_abs
        test_path = os.path.join(tmp_dir["flists"], "abs_filelist.txt")
        flist = fs.read_filelist(test_path)
        assert flist.to_list() == data_abs

    def test_read_filelist_rel(self, tmp_dir, data_rel):
        test_path = os.path.join(tmp_dir["flists"], "rel_filelist.txt")
        flist = fs.read_filelist(test_path)
        assert flist.to_list() == data_rel

    def test_save_no_ctx_from_abs(self, tmp_dir, data_abs):
        test_path = os.path.join(tmp_dir["flists"], "no_ctx_abs_filelist.txt")
        flist = fs.Filelist(data_abs)
        flist.save(test_path, output_type="na")
        with open(test_path, encoding="utf-8") as f:
            saved_data = [line.rstrip() for line in f]
            assert saved_data == [
                "sample_01.txt",
                "sample_02.txt",
                "sample_03.txt",
                "sample_04.txt",
                "sample_05.txt",
            ]

    def test_save_no_ctx_from_rel(self, tmp_dir, data_rel):
        test_path = os.path.join(tmp_dir["flists"], "no_ctx_rel_filelist.txt")
        flist = fs.Filelist(data_rel)
        flist.save(test_path, output_type="na")
        with open(test_path, encoding="utf-8") as f:
            saved_data = [line.rstrip() for line in f]
            assert saved_data == [
                "sample_01.txt",
                "sample_02.txt",
                "sample_03.txt",
                "sample_04.txt",
                "sample_05.txt",
            ]

    def test_save_no_ctx_from_na(self, tmp_dir):
        test_path = os.path.join(tmp_dir["flists"], "no_ctx_na_filelist.txt")
        flist = fs.Filelist(
            [
                "sample_01.txt",
                "sample_02.txt",
                "sample_03.txt",
                "sample_04.txt",
                "sample_05.txt",
            ],
        )
        flist.save(test_path, output_type="na")
        with open(test_path, encoding="utf-8") as f:
            saved_data = [line.rstrip() for line in f]
            assert saved_data == [
                "sample_01.txt",
                "sample_02.txt",
                "sample_03.txt",
                "sample_04.txt",
                "sample_05.txt",
            ]

    # TODO: this test is broken on MacOS
    # def test_read_filelist_no_ctx(self, tmp_dir, data_abs):
    #     test_path = os.path.join(tmp_dir["flists"], "no_ctx_na_filelist.txt")
    #     flist = fs.read_filelist(test_path)
    #     assert flist.to_list() == [
    #         os.path.relpath(os.path.join(tmp_dir["flists"], path))
    #         for path in [
    #             "sample_01.txt",
    #             "sample_02.txt",
    #             "sample_03.txt",
    #             "sample_04.txt",
    #             "sample_05.txt",
    #         ]
    #     ]

    def test_read_file_not_found(self, tmp_dir):
        with pytest.raises(FileNotFoundError, match=r"not found"):
            flist = fs.read_filelist(
                os.path.join(tmp_dir["flists"], "this_is_not_a_file")
            )

    def test_read_not_a_file(self, tmp_dir):
        with pytest.raises(TypeError, match=r"is not a valid file"):
            flist = fs.read_filelist(tmp_dir["flists"])

    def test_read_file_bad_ext(self, tmp_dir):
        with pytest.raises(TypeError, match=r"is not an accepted file extension"):
            flist = fs.read_filelist(os.path.join(tmp_dir["flists"], "bad_ext.png"))

    def test_abs_contains_abs(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist.contains(data_abs[1]) is True

    def test_abs_not_contains_abs(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist.contains("/not_a_file") is False

    def test_abs_contains_rel(self, tmp_dir, data_abs, data_rel):
        flist = fs.Filelist(data_abs)
        assert flist.contains(data_rel[2]) is True

    def test_abs_not_contains_rel(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist.contains("not_a_file") is False

    def test_rel_contains_abs(self, tmp_dir, data_abs, data_rel):
        flist = fs.Filelist(data_rel)
        assert flist.contains(data_abs[1]) is True

    def test_rel_not_contains_abs(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        assert flist.contains("/not_a_file") is False

    def test_rel_contains_rel(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        assert flist.contains(data_rel[2]) is True

    def test_rel_not_contains_rel(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        assert flist.contains("not_a_file") is False

    def test_contains_throws_typeerror(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        with pytest.raises(TypeError, match="Invalid input: filename must be a string"):
            flist.contains(1234)
        assert flist.to_list() == data_abs

    def test_iter(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        i = 0
        for fname in flist:
            assert fname == data_abs[i]
            i += 1

    def test_len(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert len(flist) == 5

    def test_idx(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist[0] == data_abs[0]
        assert flist[:] == data_abs[:]
        assert flist[-1] == data_abs[-1]
        assert flist[:-2] == data_abs[:-2]

    def test_idx_out_of_range(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        with pytest.raises(IndexError, match=r"index out of range"):
            assert flist[6]

    def test_to_list(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        assert flist.to_list() == data_abs

    def test_str_does_not_error(self, tmp_dir, data_abs):
        flist = fs.Filelist(data_abs)
        str(flist)

    def test_repr_does_not_error(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        repr(flist)


class TestCompression:
    """
    tests for reading and writing compressed filelists
    """

    def test_save_abs_compressed(self, tmp_dir, data_abs):
        """
        tests ability to save a compressed absolute filelist
        """
        test_path = os.path.join(tmp_dir["flists"], "compressed_abs.zz")
        flist = fs.Filelist(data_abs)
        flist.save(test_path, compressed=True)
        compressed_size = os.stat(test_path).st_size
        uncompressed_size = os.stat(
            os.path.join(tmp_dir["flists"], "abs_filelist.txt")
        ).st_size
        assert compressed_size < uncompressed_size

    def test_read_abs_compressed(
        self, tmp_dir, data_abs
    ):  # depends on save_abs_compressed
        """
        tests ability to read compressed absolute filelist
        """
        test_path = os.path.join(tmp_dir["flists"], "compressed_abs.zz")
        flist = fs.read_filelist(test_path, compressed=True)
        assert flist.to_list() == data_abs

    def test_save_rel_compressed(self, tmp_dir, data_rel):
        """
        tests ability to save a compressed absolute filelist
        """
        test_path = os.path.join(tmp_dir["flists"], "compressed_rel.zz")
        flist = fs.Filelist(data_rel)
        flist.save(test_path, compressed=True)
        compressed_size = os.stat(test_path).st_size
        uncompressed_size = os.stat(
            os.path.join(tmp_dir["flists"], "rel_filelist.txt")
        ).st_size
        assert 0 < compressed_size < uncompressed_size

    def test_read_rel_compressed(self, tmp_dir, data_rel):
        """
        tests ability to read compressed absolute filelist
        """
        test_path = os.path.join(tmp_dir["flists"], "compressed_rel.zz")
        flist = fs.read_filelist(test_path, compressed=True)
        assert flist.to_list() == data_rel

    def test_setitem(self, tmp_dir, data_abs, data_rel):
        # test abs path
        flist = fs.Filelist(data_abs[:2])
        flist[0] = data_abs[4]
        assert flist[0] == data_abs[4]
        flist.to_rel()
        assert flist[0] == data_rel[4]

        # test rel path
        flist[0] = data_rel[3]
        assert flist[0] == data_rel[3]
        flist.to_abs()
        assert flist[0] == data_abs[3]

    def test_setitem_slice(self, tmp_dir, data_rel, data_abs):
        # test abs path
        flist = fs.Filelist(data_abs[:3])
        flist[:3] = data_abs[2:]
        assert flist[:3] == data_abs[2:]
        flist.to_rel()
        assert flist[:3] == data_rel[2:]

        # test rel path
        flist[:3] = data_rel[:3]
        assert flist[:3] == data_rel[:3]
        flist.to_abs()
        assert flist[:3] == data_abs[:3]

    def test_setitem_error(self, tmp_dir, data_rel):
        flist = fs.Filelist(data_rel)
        with pytest.raises(
            TypeError, match=r"Invalid input: filename must be a string"
        ):
            flist[0] = 1234
