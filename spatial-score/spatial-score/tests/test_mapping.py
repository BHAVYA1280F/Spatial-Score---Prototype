from core.analysis import demo_features
from core.mapping import map_features


def test_mapping_shapes_and_ranges():
    arch = map_features(demo_features(), height_range=(3, 18))
    segs = arch["segments"]
    assert len(segs) == 28
    for s in segs:
        assert 1.5 <= s["height"] <= 18 * 1.4 + 0.1
        assert 0.05 <= s["length"] <= 12
        assert 0 <= s["openness"] <= 1
        assert s["material"] in {"concrete", "wood", "glass"}
        assert s["ribs"] >= 0


def test_empty():
    assert map_features({"tempo": 100, "segments": []})["segments"] == []


def test_zones_progression():
    arch = map_features(demo_features())
    z = [s["zone"] for s in arch["segments"]]
    assert z[0] == "intro" and z[-1] == "outro"
    assert "climax" in z
    assert set(z) <= {"intro", "rhythm", "harmony", "climax", "outro"}
    assert z.index("climax") > z.index("intro")


def test_zones_off():
    arch = map_features(demo_features(), zones=False)
    assert all(s["zone"] == "none" for s in arch["segments"])


def test_path_does_not_loop():
    import math
    arch = map_features(demo_features())
    heads = [s["heading"] for s in arch["segments"]]
    assert max(abs(h) for h in heads) < math.pi


def test_rooms_expose_the_music_that_shaped_them():
    arch = map_features(demo_features())
    assert arch["compression"] > 0
    for s in arch["segments"]:
        assert set(s["raw"]) == {"pitch_midi", "rms", "centroid", "onset_density"}
        assert set(s["norm"]) == {"pitch", "energy", "bright", "density"}
        assert set(s["base"]) == {"height", "openness", "ribs"}
        assert all(0 <= v <= 1 for v in s["norm"].values())


def test_demo_has_chart_data():
    v = demo_features()["viz"]
    assert len(v["wave"]) == len(v["energy"]) == len(v["pitch"]) == 300
    assert len(v["bands"]) == 5 and v["beats"]


def test_pavilion_dimensions():
    arch = map_features(demo_features())
    segs = arch["segments"]
    total = sum(s["length"] for s in segs)
    assert 18 <= total <= 48
    for s in segs:
        assert 1.8 <= s["height"] <= 12
        assert 5 <= s["width"] <= 13
        assert 0.7 <= s["arch_p"] <= 1.5
        assert abs(s["twist"]) <= 70
        assert s["pattern"]
