from pathlib import Path

from platforms.macos import native_cache


def test_native_key_tracks_sources_toolchain_and_architectures(tmp_path, monkeypatch):
    monkeypatch.setattr(native_cache, "ROOT", tmp_path)
    for name in native_cache.INPUTS:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    monkeypatch.setattr(native_cache.subprocess, "check_output", lambda command, **kwargs: "toolchain-1")
    initial = native_cache.cache_key()
    monkeypatch.setenv("GANNYU_MACOS_ARCHITECTURES", "arm64")
    assert native_cache.cache_key() != initial
    monkeypatch.delenv("GANNYU_MACOS_ARCHITECTURES")
    (tmp_path / native_cache.INPUTS[0]).write_text("changed native flags")
    assert native_cache.cache_key() != initial


def test_native_cache_rejects_changed_or_missing_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(native_cache, "cache_key", lambda: "fixed-toolchain")
    for name in native_cache.LIBRARIES:
        path = tmp_path / "lib" / f"lib{name}.a"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(name.encode())
    header = tmp_path / "include/rime_api.h"
    header.parent.mkdir()
    header.write_text("header")
    monkeypatch.setattr("sys.argv", ["native_cache", "write", str(tmp_path)])
    assert native_cache.main() == 0
    monkeypatch.setattr("sys.argv", ["native_cache", "check", str(tmp_path)])
    assert native_cache.main() == 0
    header.write_text("altered")
    assert native_cache.main() == 1
    header.write_text("header")
    assert native_cache.main() == 0
    (tmp_path / "lib/librime.a").unlink()
    assert native_cache.main() == 1
