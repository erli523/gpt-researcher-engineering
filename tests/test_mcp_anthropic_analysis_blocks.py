"""MCP research should pass Anthropic text blocks into the report context as text."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from gpt_researcher.llm_provider.generic.base import GenericLLMProvider
from gpt_researcher.mcp.research import MCPResearchSkill
from gpt_researcher.skills.researcher import ResearchConductor


@pytest.mark.asyncio
async def test_bound_mcp_tool_and_analysis_blocks_make_string_context(monkeypatch):
    class PublicFileTool:
        name = "read_text_file"

        async def ainvoke(self, args):
            assert args == {"path": "/public/readme.md"}
            return [{"type": "text", "text": "Public source text"}]

    response = SimpleNamespace(
        tool_calls=[{"id": "call_read", "name": "read_text_file", "args": {"path": "/public/readme.md"}}],
        content=[{"type": "thinking", "thinking": "private"},
                 {"type": "text", "text": "The file describes the project."}],
    )
    final = SimpleNamespace(tool_calls=[], content=[{"type": "text", "text": "The file describes the project."}])
    llm = SimpleNamespace(bind_tools=lambda tools: SimpleNamespace(
        ainvoke=AsyncMock(side_effect=[response, final])))
    monkeypatch.setattr(GenericLLMProvider, "from_provider", lambda *args, **kwargs: SimpleNamespace(llm=llm))
    cfg = SimpleNamespace(strategic_llm_model="fake", strategic_llm_provider="anthropic", llm_kwargs={})

    rows = await MCPResearchSkill(cfg).conduct_research_with_tools("Read public file", [PublicFileTool()])
    assert [row["href"] for row in rows] == ["mcp://read_text_file", "mcp://llm_analysis"]
    assert [row["body"] for row in rows] == ["Public source text", "The file describes the project."]

    conductor = ResearchConductor(SimpleNamespace(verbose=False, websocket=None))
    context = conductor._combine_mcp_and_web_context(
        [{"content": row["body"], "url": row["href"], "title": row["title"]} for row in rows],
        "", "Read public file")
    assert "Public source text" in context
    assert "mcp://read_text_file" in context
    assert "private" not in context


@pytest.mark.asyncio
async def test_discovery_result_can_lead_to_a_second_file_read(monkeypatch):
    class Tool:
        def __init__(self, name, content):
            self.name = name
            self.content = content
            self.ainvoke = AsyncMock(return_value=[{"type": "text", "text": content}])

    directory = Tool("list_allowed_directories", "/public")
    read = Tool("read_text_file", "Public README content")
    first = SimpleNamespace(tool_calls=[{"id": "call_list", "name": directory.name, "args": {}}], content=[])
    second = SimpleNamespace(tool_calls=[{"id": "call_read", "name": read.name,
                                          "args": {"path": "/public/readme.md"}}], content=[])
    final = SimpleNamespace(tool_calls=[], content="Summary")
    invoke = AsyncMock(side_effect=[first, second, final])
    llm = SimpleNamespace(bind_tools=lambda tools: SimpleNamespace(ainvoke=invoke))
    monkeypatch.setattr(GenericLLMProvider, "from_provider", lambda *args, **kwargs: SimpleNamespace(llm=llm))
    cfg = SimpleNamespace(strategic_llm_model="fake", strategic_llm_provider="anthropic", llm_kwargs={})

    rows = await MCPResearchSkill(cfg).conduct_research_with_tools("Read README", [directory, read])
    assert invoke.await_count == 3
    assert directory.ainvoke.await_count == 1
    read.ainvoke.assert_awaited_once_with({"path": "/public/readme.md"})
    assert [row["body"] for row in rows] == ["/public", "Public README content", "Summary"]
    assert any(getattr(message, "tool_call_id", None) == "call_list"
               for message in invoke.await_args_list[1].args[0])
