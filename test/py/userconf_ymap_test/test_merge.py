import shutil
from pathlib import Path

import pytest

from userconf_ymap.cli import main
from userconf_ymap.format import PlaceholderExpander
from userconf_ymap.merge import run_merge, run_merge_settings
from userconf_ymap.profile import SETTINGS, Pipeline
from userconf_ymap.store import NullStore

ROOT = Path(__file__).resolve().parents[3]
MYSET = ROOT / "example" / "myset.yml"


class RecordingResolver:
    def __init__(self, parts):
        self.parts = parts
        self.calls = []

    def resolve(self, source, selector):
        self.calls.append((source, selector))
        return self.parts[selector]


def test_run_merge_keeps_the_library_default():
    rendered = run_merge({"key": 123, "key2": True}, {"placeholderkey": "#{key|hex}"})

    assert rendered == {"placeholderkey": "#0x7b"}


def test_none_store_resolves_both_slots():
    resolver = RecordingResolver({
        SETTINGS.defines: {"key": 4},
        SETTINGS.maps: {"only": {"n": "{key}"}},
    })
    pipeline = Pipeline(
        profile=SETTINGS,
        resolver=resolver,
        expander=PlaceholderExpander(),
        store=NullStore(),
    )

    run_merge_settings(pipeline, "source.yml", [])

    assert resolver.calls == [
        ("source.yml", SETTINGS.defines),
        ("source.yml", SETTINGS.maps),
    ]


@pytest.mark.skipif(shutil.which("yq") is None, reason="yq is not installed")
def test_myset_merge_matches_the_example(capsys):
    main(["merge", str(MYSET)])

    assert capsys.readouterr().out.splitlines() == [
        '{"placeholderkey": "#0x7b"}',
        '{"otherkey": "123", "secondkey": "1", "thirdkey": "123.45"}',
    ]
