import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "build/macos"
MANIFEST = PAYLOAD / "ci-provenance.json"


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def source_context() -> dict[str, str]:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if commit != os.environ["GITHUB_SHA"]:
        raise ValueError("checkout does not match the workflow commit")
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    source = hashlib.sha256()
    for name in sorted(path for path in paths if path):
        source.update(name + b"\0")
        source.update(digest(ROOT / os.fsdecode(name)).encode() + b"\0")
    return {
        "commit": commit,
        "source_sha256": source.hexdigest(),
        "run_id": os.environ["GITHUB_RUN_ID"],
    }


def payload_files() -> dict[str, str]:
    bundle = PAYLOAD / "GonnyuInputMethod.app"
    smoke = PAYLOAD / "GannyuMacOSSmoke"
    if not (bundle / "Contents/MacOS/GannyuInputMethodHost").is_file() or not smoke.is_file():
        raise ValueError("missing application or smoke executable")
    if not (bundle / "Contents/Resources/rime/resource-manifest.json").is_file():
        raise ValueError("missing freshly built Rime resource manifest")
    paths = [path for path in bundle.rglob("*") if path.is_file()] + [smoke]
    return {path.relative_to(PAYLOAD).as_posix(): digest(path) for path in sorted(paths)}


def main() -> None:
    command, = sys.argv[1:]
    if command == "write":
        MANIFEST.write_text(
            json.dumps({"source": source_context(), "files": payload_files()}, indent=2) + "\n",
            encoding="utf-8",
        )
    elif command == "verify":
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if manifest["source"] != source_context():
            raise ValueError("artifact source or workflow run does not match this checkout")
        if manifest["files"] != payload_files():
            raise ValueError("artifact application or dictionary resources do not match the manifest")
        print("verified current-commit macOS application and dictionary resources")
    else:
        raise ValueError(f"unknown command: {command}")


if __name__ == "__main__":
    main()
