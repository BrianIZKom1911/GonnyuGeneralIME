#!/usr/bin/env python3
"""Stable GitHub Actions cache key for regional runtime dictionary outputs."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_PACKAGES = {
    "gannyu-input-cli",
    "gannyu-input-core",
    "gannyu-input-ffi",
    "gannyu-sanitize-binary",
    "gonnyu-resource-build",
}
CACHE_BASELINE_VERSION = "1.2.4-pre.1"


def normalized_lock(content: str) -> str:
    package = ""
    lines = []
    for line in content.splitlines():
        if line == "[[package]]":
            package = ""
        elif line.startswith('name = "') and line.endswith('"'):
            package = line[len('name = "'):-1]
        if package in WORKSPACE_PACKAGES and line.startswith("version = "):
            line = f'version = "{CACHE_BASELINE_VERSION}"'
        lines.append(line)
    return "\n".join(lines) + "\n"


def normalized_workspace_manifest(content: str) -> str:
    section = ""
    lines = []
    for line in content.splitlines():
        if line.startswith("[") and line.endswith("]"):
            section = line
        if section == "[workspace.package]" and line.startswith("version = "):
            line = f'version = "{CACHE_BASELINE_VERSION}"'
        lines.append(line)
    return "\n".join(lines) + "\n"


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    resource_paths = [
        *(ROOT / "crates/core/src").rglob("*.rs"),
        *(ROOT / "crates/resource-build/src").rglob("*.rs"),
        ROOT / "crates/core/Cargo.toml",
        ROOT / "crates/resource-build/Cargo.toml",
        ROOT / "crates/resource-build/build.rs.cache-baseline",
        ROOT / "crates/resource-build/resource_cache_key.py",
        ROOT / "resources/manifest.toml",
        *(ROOT / "resources/regions").rglob("*"),
    ]
    resource_records = []
    for path in sorted(set(path for path in resource_paths if path.is_file())):
        relative = path.relative_to(ROOT).as_posix()
        content = path.read_bytes()
        resource_records.append((relative, digest(content)))
    lock_path = ROOT / "Cargo.lock"
    normalized_lock_bytes = normalized_lock(lock_path.read_text(encoding="utf-8")).encode()
    resource_records.append(("Cargo.lock", digest(normalized_lock_bytes)))
    compiler = subprocess.check_output(["rustc", "-vV"], text=True).strip()
    resource_payload = [resource_records, compiler, platform.system(), platform.machine()]

    cargo_paths = [
        ROOT / "Cargo.toml",
        ROOT / "Cargo.lock",
        ROOT / "crates",
        ROOT / "resources/manifest.toml",
        ROOT / "resources/regions",
        ROOT / "crates/resource-build/resource_cache_key.py",
    ]
    cargo_files = []
    for path in cargo_paths:
        if path.is_dir():
            cargo_files.extend(item for item in path.rglob("*") if item.is_file())
        elif path.is_file():
            cargo_files.append(path)
    cargo_records = []
    for path in sorted(set(cargo_files)):
        relative = path.relative_to(ROOT).as_posix()
        content = path.read_bytes()
        if relative == "Cargo.toml":
            content = normalized_workspace_manifest(content.decode("utf-8")).encode()
        elif relative == "Cargo.lock":
            content = normalized_lock_bytes
        cargo_records.append((relative, digest(content)))
    cargo_payload = [cargo_records, compiler, platform.system(), platform.machine()]

    print(f"key={hashlib.sha256(json.dumps(resource_payload, sort_keys=True).encode()).hexdigest()}")
    print(f"rust_key={hashlib.sha256(json.dumps(cargo_payload, sort_keys=True).encode()).hexdigest()}")


if __name__ == "__main__":
    main()
