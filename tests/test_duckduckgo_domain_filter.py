"""Domain restriction must survive search-provider results outside requested hosts."""
from types import SimpleNamespace

import pytest

from gpt_researcher.retrievers.duckduckgo.duckduckgo import Duckduckgo


def test_restricted_query_filters_unrelated_and_lookalike_hosts():
    calls = []

    def search(query, **kwargs):
        calls.append((query, kwargs))
        return [
            {"href": "https://docs.langchain.com/oss/python/langgraph/persistence", "body": "real"},
            {"href": "https://docs.langchain.com.evil.test/imitate", "body": "imitation"},
            {"href": "https://other.example.com/article", "body": "other"},
            {"href": "https://sub.docs.langchain.com/page", "body": "subdomain"},
        ]

    retriever = Duckduckgo.__new__(Duckduckgo)
    retriever.ddg = SimpleNamespace(text=search)
    retriever.query = "LangGraph persistence"
    retriever.query_domains = ["docs.langchain.com"]
    rows = retriever.search(max_results=3)
    assert calls == [("LangGraph persistence",
                      {"region": "wt-wt", "max_results": 9})]
    assert [row["body"] for row in rows] == ["real", "subdomain"]


def test_domain_validation_rejects_query_injection():
    with pytest.raises(ValueError):
        Duckduckgo._domain_name("example.com OR site:evil.test")
    assert Duckduckgo._domain_name("Docs.Langchain.Com.") == "docs.langchain.com"


def test_unrestricted_query_still_uses_original_result_cap():
    calls = []
    retriever = Duckduckgo.__new__(Duckduckgo)
    retriever.ddg = SimpleNamespace(text=lambda query, **kwargs: calls.append((query, kwargs)) or [])
    retriever.query = "research"
    retriever.query_domains = []
    assert retriever.search(max_results=5) == []
    assert calls == [("research", {"region": "wt-wt", "max_results": 5})]
