from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from piranha_agent.cli import main


def test_monitor_command_registered():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "monitor" in result.output


def test_monitor_constructs_realtime_monitor_with_options():
    runner = CliRunner()
    with patch("piranha_agent.realtime.RealtimeMonitor") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        result = runner.invoke(
            main,
            ["monitor", "--host", "0.0.0.0", "--port", "9000"],
        )

        assert result.exit_code == 0
        mock_cls.assert_called_once_with(
            host="0.0.0.0", port=9000, dashboard_path=None, db_path=None
        )
        mock_instance.start.assert_called_once_with(blocking=True)


def test_monitor_defaults_to_localhost_8080():
    runner = CliRunner()
    with patch("piranha_agent.realtime.RealtimeMonitor") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        result = runner.invoke(main, ["monitor"])

        assert result.exit_code == 0
        mock_cls.assert_called_once_with(
            host="127.0.0.1", port=8080, dashboard_path=None, db_path=None
        )
