from lib1 import metadata


def test_metadata():
    m = metadata()
    assert isinstance(m, dict)
    assert m.get("library") == "lib1"
