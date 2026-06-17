from research_agent.config import AppConfig


def test_config_reads_llm_timeout(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "45")
    config = AppConfig.from_env()
    assert config.llm_timeout_seconds == 45


def test_config_reads_report_timeout_and_max_chars(monkeypatch):
    monkeypatch.setenv("REPORT_TIMEOUT_SECONDS", "180")
    monkeypatch.setenv("REPORT_MAX_CHARS", "40000")
    config = AppConfig.from_env()
    assert config.report_timeout_seconds == 180
    assert config.report_max_chars == 40000
