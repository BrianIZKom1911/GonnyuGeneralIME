from pathlib import Path

from platforms.rime import build_cache


def test_content_fingerprints_ignore_mtime_and_separate_inputs(tmp_path: Path):
    first = tmp_path / 'first'
    second = tmp_path / 'second'
    first.write_bytes(b'first input')
    second.write_bytes(b'second input')
    first_key = build_cache.fingerprint(tmp_path, [first], 'generator-v1')
    second_key = build_cache.fingerprint(tmp_path, [second], 'generator-v1')
    first.touch()
    assert build_cache.fingerprint(tmp_path, [first], 'generator-v1') == first_key
    first.write_bytes(b'updated input')
    assert build_cache.fingerprint(tmp_path, [first], 'generator-v1') != first_key
    assert build_cache.fingerprint(tmp_path, [second], 'generator-v1') == second_key
    assert build_cache.fingerprint(tmp_path, [second], 'generator-v2') != second_key


def test_cache_rejects_missing_and_corrupt_outputs(tmp_path: Path):
    payload = tmp_path / 'payload.bin'
    payload.write_bytes(b'compiled bytes')
    stamp = tmp_path / 'cache.json'
    build_cache.save(stamp, tmp_path, 'key', [payload], {'entries': 1})
    assert build_cache.load(stamp, tmp_path, 'key')['counts'] == {'entries': 1}
    assert build_cache.load(stamp, tmp_path, 'different') is None
    payload.write_bytes(b'corrupt')
    assert build_cache.load(stamp, tmp_path, 'key') is None
    payload.unlink()
    assert build_cache.load(stamp, tmp_path, 'key') is None
