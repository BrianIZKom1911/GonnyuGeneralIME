from pathlib import Path

import pytest

from platforms.rime.mobile import build_resources


@pytest.mark.parametrize("failure", [False, True])
def test_resources_move_after_success_and_preserve_old_output_on_failure(tmp_path, monkeypatch, failure):
    output = tmp_path / "resources"
    output.mkdir()
    (output / "old").write_text("retain until deployment succeeds")
    deployer = tmp_path / "rime_deployer"
    deployer.touch()
    monkeypatch.setattr(build_resources, "active_regions", lambda: ["lancong"])
    calls = []

    def run(*command):
        calls.append(command)
        if command[0] == str(deployer):
            if failure:
                raise RuntimeError("deployment failed")
            prebuilt = Path(command[-1])
            prebuilt.mkdir(parents=True)
            (prebuilt / "built").write_text("compiled")
        else:
            shared = Path(command[-1])
            shared.mkdir()
            (shared / "source").write_text("generated")

    monkeypatch.setattr(build_resources, "run", run)
    monkeypatch.setattr(build_resources.shutil, "copytree", lambda *args, **kwargs: pytest.fail("resource staging must move rather than duplicate"))
    if failure:
        with pytest.raises(RuntimeError, match="deployment failed"):
            build_resources.build(output, deployer)
        assert (output / "old").is_file()
    else:
        build_resources.build(output, deployer)
        assert (output / "shared/source").read_text() == "generated"
        assert (output / "prebuilt/built").read_text() == "compiled"
        assert (output / "resource-manifest.json").is_file()
        assert not (output / "old").exists()
    assert len(calls) == 2
    assert not list(tmp_path.glob("gonnyu-rime-mobile-*"))
