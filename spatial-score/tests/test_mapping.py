from core.analysis import demo_features
from core.mapping import map_features


def test_mapping_shapes_and_ranges():
    arch = map_features(demo_features(), height_range=(3, 18))
    segs = arch["segments"]
    assert len(segs) == 28
    for s in segs:
        assert 3 <= s["height"] <= 18
        assert 2 <= s["length"] <= 12
        assert 0 <= s["openness"] <= 1
        assert s["material"] in {"concrete", "wood", "glass"}
        assert s["ribs"] >= 2


def test_empty():
    assert map_features({"tempo": 100, "segments": []})["segments"] == []
