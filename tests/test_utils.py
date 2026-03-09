from echochamber.utils import apply_chaos, recursive_layers, shallow_copy, deep_copy


def test_apply_chaos_changes_text():
    s = "Helloooo!!!"
    out = apply_chaos(s, intensity=2)
    assert isinstance(out, str)
    assert out != s


def test_recursive_layers():
    def f(x: str) -> str:
        return x + "!"

    assert recursive_layers("a", f, 3) == "a!!!"


def test_shallow_vs_deep_copy():
    obj = {"tags": ["a", "b"]}
    s = shallow_copy(obj)
    d = deep_copy(obj)

    obj["tags"].append("c")

    # shallow copy shares nested list
    assert s["tags"] == ["a", "b", "c"]
    # deep copy does not
    assert d["tags"] == ["a", "b"]


from echochamber.utils import EngineConfig, now_string


def test_engine_config_is_hashable():
    cfg = EngineConfig()
    d = {cfg: "value"}
    assert d[cfg] == "value"


def test_now_string_default_format():
    result = now_string()
    assert len(result) == 16  # "YYYY-MM-DD HH:MM"


def test_recursive_layers_zero():
    result = recursive_layers("hello", lambda x: x + "!", 0)
    assert result == "hello"


def test_apply_chaos_zero_intensity():
    result = apply_chaos("Hello!!!", intensity=0)
    assert result == "Hello!!!"