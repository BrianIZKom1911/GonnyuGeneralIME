from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def fingerprint(root: Path, paths: list[Path], options: str) -> str:
    records = [(path.relative_to(root).as_posix(), digest(path)) for path in sorted(set(paths))]
    return hashlib.sha256(json.dumps([options, records], sort_keys=True).encode()).hexdigest()


def load(stamp: Path, root: Path, key: str) -> dict | None:
    try:
        data = json.loads(stamp.read_text())
        if data['key'] != key or not data['files']:
            return None
        for name, checksum in data['files'].items():
            path = root / name
            if not path.resolve().is_relative_to(root.resolve()) or digest(path) != checksum:
                return None
        return data
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def save(stamp: Path, root: Path, key: str, files: list[Path], counts: dict) -> None:
    data = {'key': key, 'counts': counts, 'files': {
        path.relative_to(root).as_posix(): digest(path) for path in sorted(files)
    }}
    temporary = stamp.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, sort_keys=True) + '\n')
    temporary.replace(stamp)
