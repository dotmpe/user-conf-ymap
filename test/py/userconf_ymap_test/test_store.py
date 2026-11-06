import json

import pytest

from userconf_ymap.leaf import ConfigError, ContextError
from userconf_ymap.store import JsonStore, NullStore, build_json_store


def test_null_store_loads_nothing():
    store = NullStore()

    assert not hasattr(store, "document")


def test_json_store_retains_the_document(tmp_path):
    path = tmp_path / "parts.json"
    document = {
        "profile": "settings",
        "definitions": {"key": 123},
        "maps": {"myconfigA": {"placeholderkey": "{key}"}},
    }
    path.write_text(json.dumps(document), encoding="utf-8")

    store = JsonStore(str(path))

    assert store.path == str(path)
    assert store.document == document


def test_json_store_retains_a_non_object_document(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")

    assert JsonStore(str(path)).document == []


def test_json_store_requires_a_path_and_valid_json(tmp_path):
    with pytest.raises(ConfigError, match="store_from"):
        build_json_store(None)

    missing = tmp_path / "missing.json"
    with pytest.raises(ContextError):
        JsonStore(str(missing))

    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid JSON"):
        JsonStore(str(broken))
