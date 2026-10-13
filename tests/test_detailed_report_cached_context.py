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


@pytest.mark.asyncio
async def test_detailed_subtopic_fails_when_parent_has_no_scraped_pages(monkeypatch):
    detailed = DetailedReport(query="checkpoint review", report_type="detailed_report",
                              report_source="web", source_urls=["https://example.org/source"])
    detailed.global_context = ["Earlier context was not a scraped source page"]
    async def no_new_pages(self):
        self.context = ""
        return ""
    monkeypatch.setattr(GPTResearcher, "conduct_research", no_new_pages)
    with pytest.raises(RuntimeError, match="No scraped source content"):
        await detailed._get_subtopic_report({"task": "human review"})
