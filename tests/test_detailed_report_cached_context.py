"""A deduped source URL must not turn a detailed subtopic into an empty report."""
import pytest
from gpt_researcher import GPTResearcher
from backend.report_type.detailed_report.detailed_report import DetailedReport


@pytest.mark.asyncio
async def test_reuse_real_parent_pages_for_subtopic_when_urls_were_visited(monkeypatch):
    monkeypatch.setenv("CONTEXT_FILTER", "keyword")
    detailed = DetailedReport(query="checkpoint review", report_type="detailed_report",
                              report_source="web")
    detailed.gpt_researcher.research_sources = [{
        "url": "https://docs.langchain.com/oss/python/langgraph/checkpointers",
        "title": "Checkpointers",
        "raw_content": "Checkpointers persist state and permit human review after an interrupt. " * 80,
    }]
    subtopic = GPTResearcher(query="human review after interrupt", report_type="subtopic_report")
    pages = detailed.gpt_researcher.get_research_sources()
    subtopic.context = await subtopic.context_manager.get_similar_content_by_query(subtopic.query, pages)
    assert "human review after an interrupt" in subtopic.context
    assert "docs.langchain.com" in subtopic.context


def test_string_context_remains_one_context_item():
    detailed = DetailedReport(query="checkpoint review", report_type="detailed_report", report_source="web")
    assert detailed._hashable_context("documented checkpoint") == ["documented checkpoint"]
