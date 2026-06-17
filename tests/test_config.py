from research_agent.config import AppConfig


def test_config_reads_llm_timeout(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "45")
    config = AppConfig.from_env()
    assert config.llm_timeout_seconds == 45


def test_config_reads_report_timeout_and_max_chars(monkeypatch):
    monkeypatch.setenv("REPORT_TIMEOUT_SECONDS", "180")
    monkeypatch.setenv("REPORT_MAX_CHARS", "40000")
    monkeypatch.setenv("REPORT_FALLBACK_MODEL", "fallback")
    monkeypatch.setenv("REPORT_FALLBACK_MAX_CHARS", "12000")
    monkeypatch.setenv("REPORT_MAX_RETRIES", "2")
    monkeypatch.setenv("REPORT_CONSECUTIVE_FAILURE_LIMIT", "3")
    config = AppConfig.from_env()
    assert config.report_timeout_seconds == 180
    assert config.report_max_chars == 40000
    assert config.report_fallback_model == "fallback"
    assert config.report_fallback_max_chars == 12000
    assert config.report_max_retries == 2
    assert config.report_consecutive_failure_limit == 3
