import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
INPUTS = (
    "platforms/macos/build_rime_engine.sh",
    "platforms/macos/native_cache.py",
    "platforms/rime/mobile/engine-lock.json",
    "platforms/rime/mobile/boost_regex/CMakeLists.txt",
)
LIBRARIES = ("rime", "leveldb", "marisa", "opencc", "yaml-cpp", "glog", "boost_regex")


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def cache_key() -> str:
    identity = {name: digest(ROOT / name) for name in INPUTS}
    identity["architectures"] = os.environ.get("GANNYU_MACOS_ARCHITECTURES", "arm64;x86_64")
    identity["deployment_target"] = os.environ.get("GANNYU_MACOS_DEPLOYMENT_TARGET", "13.0")
    for name in ("CC", "CXX", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "SDKROOT"):
        identity[name] = os.environ.get(name, "")
    for name, command in (
        ("compiler", ["xcrun", "clang++", "--version"]),
        ("sdk", ["xcrun", "--sdk", "macosx", "--show-sdk-version"]),
        ("sdk_path", ["xcrun", "--sdk", "macosx", "--show-sdk-path"]),
        ("cmake", ["cmake", "--version"]),
    ):
        identity[name] = subprocess.check_output(command, text=True).strip()
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def records(prefix: Path) -> dict[str, str]:
    for name in LIBRARIES:
        if not (prefix / "lib" / f"lib{name}.a").is_file():
            raise FileNotFoundError(name)
    if not (prefix / "include/rime_api.h").is_file():
        raise FileNotFoundError("rime_api.h")
    return {
        path.relative_to(prefix).as_posix(): digest(path)
        for path in sorted(prefix.rglob("*"))
        if path.is_file() and path.name != ".gannyu-native-cache.json"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("key", "check", "write"))
    parser.add_argument("prefix", nargs="?", type=Path)
    args = parser.parse_args()
    key = cache_key()
    if args.action == "key":
        print(key)
        return 0
    if args.prefix is None:
        parser.error("prefix is required")
    stamp = args.prefix / ".gannyu-native-cache.json"
    try:
        current = {"key": key, "files": records(args.prefix)}
        if args.action == "write":
            stamp.write_text(json.dumps(current, sort_keys=True) + "\n")
            return 0
        return 0 if json.loads(stamp.read_text()) == current else 1
    except (OSError, ValueError):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
