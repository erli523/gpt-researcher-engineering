"""Regression for real Anthropic content blocks and mixed streamed output."""
import asyncio
from types import SimpleNamespace
import pytest
from gpt_researcher.llm_provider.generic.base import GenericLLMProvider


def test_text_blocks_exclude_private_reasoning_and_tools():
    content = [{"type": "thinking", "thinking": "private"},
               {"type": "text", "text": '{"agent":'},
               {"type": "tool_use", "input": {"text": "not answer"}},
               {"type": "text", "text": '"researcher"}'}, "\n"]
    assert GenericLLMProvider._text_content(content) == '{"agent":"researcher"}\n'


def test_strings_empty_lists_and_invalid_top_level():
    assert GenericLLMProvider._text_content("old format") == "old format"
    assert GenericLLMProvider._text_content([]) == ""
    with pytest.raises(TypeError):
        GenericLLMProvider._text_content({"text": "invalid"})


def test_nonstream_blocks_preserve_usage():
    class LLM:
        async def ainvoke(self, messages, **kwargs):
            return SimpleNamespace(content=[{"type": "text", "text": "answer"}],
                usage_metadata={"input_tokens": 2, "output_tokens": 1}, response_metadata={})
    provider = GenericLLMProvider(LLM(), verbose=False)
    assert asyncio.run(provider.get_chat_response([], False)) == "answer"
    assert provider.last_usage_metadata == {"input_tokens": 2, "output_tokens": 1}


def test_streaming_mixed_blocks_and_final_usage():
    class LLM:
        async def astream(self, messages, **kwargs):
            for content, usage in [([{"type": "thinking", "thinking": "private"}], None),
                    ([{"type": "text", "text": "first\n"}], None), ("second", None),
                    ([], {"input_tokens": 5, "output_tokens": 3})]:
                yield SimpleNamespace(content=content, usage_metadata=usage, response_metadata={})
    class Socket:
        def __init__(self):
            self.events = []
        async def send_json(self, event):
            self.events.append(event)
    provider, socket = GenericLLMProvider(LLM(), verbose=False), Socket()
    assert asyncio.run(provider.stream_response([], socket)) == "first\nsecond"
    assert [event["output"] for event in socket.events] == ["first\n", "second"]
    assert provider.last_usage_metadata["output_tokens"] == 3
