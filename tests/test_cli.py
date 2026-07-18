import pytest

from job_agent.cli import main


def test_sources_list_reports_manual_capture(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sources", "list"]) == 0
    assert capsys.readouterr().out.splitlines() == ["manual"]
