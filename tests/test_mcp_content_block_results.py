"""Preserve real adapter text blocks and existing search result formats."""
from gpt_researcher.mcp.research import MCPResearchSkill


def test_unwrapped_text_preserves_unicode_quotes_and_line_endings():
    body = "中文工具正文\r\nA 'quoted' line\nLast line"
    blocks = [{"type": "text", "text": body, "id": "adapter-generated-id"}]
    rows = MCPResearchSkill(cfg=None)._process_tool_result("read_text_file", blocks)
    assert len(rows) == 1
    assert rows[0]["body"] == body
    assert rows[0]["href"] == "mcp://read_text_file"


def test_multiple_text_blocks_are_joined_as_existing_wrapper_contract():
    blocks = [{"type": "text", "text": "First paragraph"},
              {"type": "text", "text": "第二段"}]
    rows = MCPResearchSkill(cfg=None)._process_tool_result("read", blocks)
    assert [row["body"] for row in rows] == ["First paragraph\n\n第二段"]


def test_search_results_keep_source_fields():
    search = [{"title": "Official docs", "url": "https://example.org/docs", "content": "Document body"}]
    rows = MCPResearchSkill(cfg=None)._process_tool_result("search", search)
    assert rows == [{"title": "Official docs", "href": "https://example.org/docs", "body": "Document body"}]


def test_structured_wrapper_keeps_sources_and_body():
    result = {"structured_content": {"results": [
        {"title": "Reference", "href": "https://example.org/reference", "body": "Source content"}
    ]}}
    rows = MCPResearchSkill(cfg=None)._process_tool_result("search", result)
    assert rows == result["structured_content"]["results"]


def test_empty_list_stays_empty():
    assert MCPResearchSkill(cfg=None)._process_tool_result("read", []) == []
