import requests

from research_agent.collectors.huggingface import HuggingFacePapersCollector


def test_huggingface_collector_ignores_numeric_paper_links(monkeypatch):
    html = """
    <html><body>
      <main>
        <article>
          <a href="/papers/2606.12345">Useful Circuit Tracing for Language Models</a>
          <p>A mechanistic interpretability abstract.</p>
        </article>
        <a href="/papers/2606.11111">1</a>
        <a href="/papers/2606.22222">2</a>
      </main>
    </body></html>
    """

    class Response:
        text = html

        def raise_for_status(self):
            return None

    def fake_get(*args, **kwargs):
        return Response()

    session = requests.Session()
    monkeypatch.setattr(session, "get", fake_get)

    candidates = HuggingFacePapersCollector(session).collect(lookback_days=30)

    assert [candidate.title for candidate in candidates] == ["Useful Circuit Tracing for Language Models"]
