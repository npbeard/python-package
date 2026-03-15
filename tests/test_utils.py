import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UTILS_PATH = ROOT / "echochamber" / "utils.py"
SPEC = importlib.util.spec_from_file_location("echochamber.utils", UTILS_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Could not load module from {UTILS_PATH}")

utils = importlib.util.module_from_spec(SPEC)
sys.modules["echochamber.utils"] = utils
SPEC.loader.exec_module(utils)

apply_chaos = utils.apply_chaos
recursive_layers = utils.recursive_layers
shallow_copy = utils.shallow_copy
deep_copy = utils.deep_copy


def test_apply_chaos_changes_text():
    s = "Helloooo!!!"
    out = apply_chaos(s, intensity=2)
    assert isinstance(out, str)
    assert out != s


def test_recursive_layers():
    def f(x: str) -> str:
        return f"{x}!"

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
