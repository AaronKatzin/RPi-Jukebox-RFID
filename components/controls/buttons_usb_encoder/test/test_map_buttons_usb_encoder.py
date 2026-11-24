import ast
from pathlib import Path

# The mapper runs interactively at import time, so load only the normalizer.
SOURCE = Path(__file__).resolve().parents[1] / "map_buttons_usb_encoder.py"


def _load_normalize_button_keycode():
    tree = ast.parse(SOURCE.read_text())
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "normalize_button_keycode"
    ]
    assert len(functions) == 1
    module = ast.Module(body=functions, type_ignores=[])
    namespace = {}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["normalize_button_keycode"]


normalize_button_keycode = _load_normalize_button_keycode()


def test_string_keycode_is_unchanged():
    assert normalize_button_keycode("KEY_A") == "KEY_A"


def test_list_keycode_is_sorted_and_joined():
    assert normalize_button_keycode(["KEY_B", "KEY_A"]) == "KEY_A-KEY_B"


def test_tuple_keycode_can_be_concatenated_with_args_suffix():
    # evdev may report aliases as a tuple. Concatenating that tuple with
    # "_args" raised TypeError: can only concatenate tuple (not "str") to tuple.
    button_string = normalize_button_keycode(("KEY_LEFT", "BTN_LEFT"))
    assert button_string == "BTN_LEFT-KEY_LEFT"
    assert button_string + "_args" == "BTN_LEFT-KEY_LEFT_args"


def test_single_item_tuple_keycode_becomes_string():
    button_string = normalize_button_keycode(("KEY_ENTER",))
    assert button_string + "_args" == "KEY_ENTER_args"


def test_mapper_normalizes_keycode_before_args_suffix():
    source = SOURCE.read_text()
    normalize_at = source.index("button_string = normalize_button_keycode(keyevent.keycode)")
    args_at = source.index('button_map[button_string + "_args"]')
    assert normalize_at < args_at
