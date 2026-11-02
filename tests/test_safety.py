
"""Offline tests for the agent's calculator and file sandbox. Run: pytest tests"""

import pathlib
import sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from common.safety import resolve_in_workspace, safe_eval  # noqa: E402


def test_basic_math():
    assert safe_eval("(120*1.08)/3") == pytest.approx(43.2)
    assert safe_eval("sqrt(144)+2**5") == 44


@pytest.mark.parametrize(
    "bad",
    [
        "__import__('os').system('ls')",
        "open('x')",
        "().__class__",
        "2**100000",
        "1/0",
    ],
)
def test_rejects_dangerous_or_invalid(bad):
    with pytest.raises(Exception):
        safe_eval(bad)


def test_workspace_sandbox(tmp_path):
    (tmp_path / "ok.txt").write_text("hi")

    assert resolve_in_workspace(tmp_path, "ok.txt").name == "ok.txt"

    with pytest.raises(PermissionError):
        resolve_in_workspace(tmp_path, "../secret.txt")

    with pytest.raises(PermissionError):
        resolve_in_workspace(tmp_path, "/etc/passwd")
