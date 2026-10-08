"""Tests for the Docker entrypoint scripts."""

import os
import stat
import subprocess
from pathlib import Path

import pytest

from shared.config import load_config

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = ["labram", "reve", "bendr"]


def _run_entrypoint(model: str, tmp_path: Path, *args: str) -> list[str]:
    """Run an entrypoint with a stub python3 and return the arguments it received."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    args_file = tmp_path / "args.txt"
    stub = bin_dir / "python3"
    stub.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{args_file}"\n')
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)

    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    subprocess.run(
        ["bash", str(REPO_ROOT / model / "entrypoint.sh"), *args, "in", "out"],
        env=env,
        check=True,
        capture_output=True,
    )
    return args_file.read_text().splitlines()


@pytest.mark.parametrize("model", MODELS)
def test_entrypoint_defaults_to_bundled_config(model, tmp_path):
    passed = _run_entrypoint(model, tmp_path)
    assert passed[passed.index("--config") + 1] == f"/app/{model}/config.yaml"


@pytest.mark.parametrize("model", MODELS)
def test_entrypoint_uses_given_config(model, tmp_path):
    passed = _run_entrypoint(model, tmp_path, "--config", "/data/custom.yaml")
    assert passed[passed.index("--config") + 1] == "/data/custom.yaml"


@pytest.mark.parametrize("model", MODELS)
def test_bundled_config_loads(model):
    config = load_config(REPO_ROOT / model / "config.yaml")
    assert config.model.model_name == model
