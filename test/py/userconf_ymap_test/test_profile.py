import json
import shutil

import pytest

from userconf_ymap.cli import main, parse_args, pipeline_for_merge
from userconf_ymap.format import PlaceholderExpander
from userconf_ymap.leaf import ConfigError, ContextError
from userconf_ymap.profile import SETTINGS, build_pipeline, read_document_profile, resolve_profile
from userconf_ymap.resolve import YqResolver
from userconf_ymap.store import JsonStore, NullStore


def test_settings_pipeline_uses_builtin_components():
    pipeline = build_pipeline(SETTINGS)

    assert isinstance(pipeline.resolver, YqResolver)
    assert isinstance(pipeline.expander, PlaceholderExpander)
    assert isinstance(pipeline.store, NullStore)
    assert pipeline.profile.defines == 'first(.definitions[]|select(type=="object"))'
    assert pipeline.profile.maps == ".maps"
    assert set(pipeline.expander.filters) == {"str", "hex", "bit", "revbit"}


def test_cli_selector_beats_env_and_env_beats_preset():
    profile = resolve_profile(
        name="settings",
        defines=".from-cli",
        maps=None,
        resolver=None,
        expander=None,
        store=None,
        store_from=None,
        document_name="ignored",
        env="other,.from-env,.maps-env",
    )

    assert profile.name == "settings"
    assert profile.defines == ".from-cli"
    assert profile.maps == ".maps-env"
    assert profile.resolver == "yq"


def test_omitted_name_uses_document_then_settings():
    named = resolve_profile(
        name=None,
        defines=None,
        maps=None,
        resolver=None,
        expander=None,
        store=None,
        store_from=None,
        document_name="settings",
        env=None,
    )
    fallback = resolve_profile(
        name=None,
        defines=None,
        maps=None,
        resolver=None,
        expander=None,
        store=None,
        store_from=None,
        document_name=None,
        env=None,
    )

    assert named.name == "settings"
    assert fallback.name == "settings"
    assert fallback.defines == SETTINGS.defines


def test_unknown_component_names_raise():
    with pytest.raises(ConfigError, match="unknown profile"):
        resolve_profile(
            name="srgb-hex-names",
            defines=None,
            maps=None,
            resolver=None,
            expander=None,
            store=None,
            store_from=None,
            document_name=None,
            env=None,
        )
    with pytest.raises(ConfigError, match="unknown resolver"):
        build_pipeline(SETTINGS.__class__(**{**SETTINGS.__dict__, "resolver": "nope"}))
    with pytest.raises(ConfigError, match="unknown expander"):
        build_pipeline(replace_profile(expander="nope"))
    with pytest.raises(ConfigError, match="unknown store"):
        build_pipeline(replace_profile(store="missing"))
    with pytest.raises(ConfigError, match="unknown filter"):
        build_pipeline(replace_profile(filters=("nope",)))


def test_env_name_skips_document_read(tmp_path):
    missing = tmp_path / "absent.yml"
    args = parse_args(["merge", "--from", "json", str(missing)])

    pipeline = pipeline_for_merge(args, {"UC_YMAP_PROFILE": "settings,.defs"})

    assert pipeline.profile.name == "settings"
    assert pipeline.profile.defines == ".defs"
    assert not missing.exists()


def test_document_profile_from_json(tmp_path):
    path = tmp_path / "doc.json"
    path.write_text(json.dumps({"profile": "settings", "extra": 1}), encoding="utf-8")
    args = parse_args(["merge", "--from", "json", str(path)])

    assert read_document_profile(str(path), "json") == "settings"
    pipeline = pipeline_for_merge(args, {})

    assert pipeline.profile.name == "settings"


def test_missing_document_profile_uses_settings(tmp_path):
    path = tmp_path / "doc.json"
    path.write_text("{}", encoding="utf-8")

    assert read_document_profile(str(path), "json") is None
    args = parse_args(["merge", "--from", "json", str(path)])
    assert pipeline_for_merge(args, {}).profile.name == "settings"


def test_json_store_flag_builds_json_backend(tmp_path):
    path = tmp_path / "parts.json"
    path.write_text(json.dumps({"definitions": {"key": 1}, "maps": {}}), encoding="utf-8")
    args = parse_args([
        "merge", "--profile", "settings", "--store", "json", "--store-from", str(path), "unused.yml",
    ])

    pipeline = pipeline_for_merge(args, {})

    assert isinstance(pipeline.store, JsonStore)
    assert pipeline.store.document == {"definitions": {"key": 1}, "maps": {}}


def test_main_reports_unknown_store(capsys):
    with pytest.raises(SystemExit) as caught:
        main(["merge", "--profile", "settings", "--store", "missing", "unused.yml"])

    assert caught.value.code == 1
    assert "unknown store" in capsys.readouterr().err


@pytest.mark.skipif(shutil.which("yq") is None, reason="yq is not installed")
def test_yaml_prelude_reads_profile_scalar(tmp_path):
    path = tmp_path / "doc.yml"
    path.write_text("profile: settings\n", encoding="utf-8")

    assert read_document_profile(str(path), None) == "settings"


def test_yaml_prelude_failure_is_context_error(tmp_path, monkeypatch):
    path = tmp_path / "doc.yml"
    path.write_text("profile: settings\n", encoding="utf-8")
    monkeypatch.setattr("userconf_ymap.profile.subprocess.run", _explode)

    with pytest.raises(ContextError):
        read_document_profile(str(path), "yaml")


def replace_profile(**changes):
    from dataclasses import replace

    return replace(SETTINGS, **changes)


def _explode(*_args, **_kwargs):
    raise OSError("yq missing")
