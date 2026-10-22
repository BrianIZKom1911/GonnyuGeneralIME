import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_mobile_preparation_uses_the_configured_host_tool_directory(tmp_path: Path) -> None:
    scripts = tmp_path / "platforms/rime/mobile"
    scripts.mkdir(parents=True)
    shutil.copyfile(ROOT / "platforms/rime/mobile/prepare_resources.sh", scripts / "prepare_resources.sh")
    (scripts / "build_host.sh").write_text('set -eu\nmkdir -p "$GANNYU_RIME_MOBILE_BUILD_ROOT/build/bin"\nprintf host > "$GANNYU_RIME_MOBILE_BUILD_ROOT/build/bin/rime_deployer"\n')
    (scripts / "build_resources.py").write_text('''import argparse
import os
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path)
parser.add_argument("--deployer", type=Path)
args = parser.parse_args()
expected = Path(os.environ["GANNYU_RIME_MOBILE_BUILD_ROOT"]) / "build/bin/rime_deployer"
assert args.deployer == expected and args.deployer.read_text() == "host"
args.output.mkdir(parents=True)
(args.output / "verified").write_text(str(args.deployer))
''')
    host = tmp_path / "ios isolated host"
    output = tmp_path / "resources"
    env = dict(os.environ, PYTHON_BIN=sys.executable, GANNYU_RIME_MOBILE_BUILD_ROOT=str(host), GANNYU_MOBILE_RESOURCE_ROOT=str(output))
    subprocess.run(["bash", str(scripts / "prepare_resources.sh")], env=env, check=True, capture_output=True, text=True)
    assert (output / "verified").read_text() == str(host / "build/bin/rime_deployer")
