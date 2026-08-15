import json
import subprocess
from unittest.mock import MagicMock, patch

from piranha_agent.skills.model_compat import check_model_compatibility

_SAMPLE_OUTPUT = json.dumps({
    "hardware": {"description": "Apple M1 (8GB Unified Memory)", "tier": "low", "maxSize": 4},
    "topPicks": {
        "best": {
            "variant": {"tag": "qwen3:1.7b-q8_0", "params_b": 1.7, "size_gb": 1.7},
            "score": {"final": 85},
        }
    },
    "insights": [
        {"type": "info", "message": "Apple Silicon detected."},
        {"type": "success", "message": "Excellent match found!"},
    ],
})

_CLOUD_ONLY_OUTPUT = json.dumps({
    "hardware": {"description": "Apple M1 (8GB Unified Memory)", "tier": "low", "maxSize": 4},
    "topPicks": {
        "best": {
            "variant": {"tag": "kimi-k2:1t-cloud", "params_b": None, "size_gb": None},
            "score": {"final": 66},
        }
    },
    "insights": [{"type": "warning", "message": "Limited options for your hardware."}],
})


def test_binary_not_installed():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value=None):
        result = check_model_compatibility("qwen3")
    assert "npm install -g llm-checker" in result


def test_local_match_found():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value="/usr/local/bin/llm-checker"):
        with patch("piranha_agent.skills.model_compat.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=_SAMPLE_OUTPUT, stderr="")
            result = check_model_compatibility("qwen3", use_case="coding")

    assert "Apple M1" in result
    assert "qwen3:1.7b-q8_0" in result
    assert "1.7GB" in result

    args = mock_run.call_args[0][0]
    assert args[:2] == ["llm-checker", "search"]
    assert "qwen3" in args
    assert "--use-case" in args and "coding" in args


def test_cloud_only_model_reported_clearly():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value="/usr/local/bin/llm-checker"):
        with patch("piranha_agent.skills.model_compat.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=_CLOUD_ONLY_OUTPUT, stderr="")
            result = check_model_compatibility("kimi")

    assert "cloud-only" in result
    assert "too large to run on this machine" in result


def test_cli_failure_surfaces_stderr():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value="/usr/local/bin/llm-checker"):
        with patch("piranha_agent.skills.model_compat.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="network error")
            result = check_model_compatibility("qwen3")

    assert "llm-checker failed" in result
    assert "network error" in result


def test_timeout_handled():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value="/usr/local/bin/llm-checker"):
        with patch(
            "piranha_agent.skills.model_compat.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="llm-checker", timeout=60),
        ):
            result = check_model_compatibility("qwen3")

    assert "timed out" in result


def test_invalid_json_handled():
    with patch("piranha_agent.skills.model_compat.shutil.which", return_value="/usr/local/bin/llm-checker"):
        with patch("piranha_agent.skills.model_compat.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="not json", stderr="")
            result = check_model_compatibility("qwen3")

    assert "Could not parse" in result
