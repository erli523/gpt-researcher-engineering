from langchain_core.documents import Document
import pytest

from gpt_researcher.document.langchain_document import LangChainDocumentLoader


@pytest.mark.asyncio
async def test_standard_source_metadata_is_preserved():
    rows = await LangChainDocumentLoader([
        Document(page_content="public content", metadata={"source": "public.md"})
    ]).load()
    assert rows == [{"raw_content": "public content", "url": "public.md"}]


@pytest.mark.asyncio
async def test_requested_metadata_key_takes_precedence_then_falls_back():
    rows = await LangChainDocumentLoader([
        Document(page_content="one", metadata={"title": "Title", "source": "source.md"}),
        Document(page_content="two", metadata={"source": "fallback.md"}),
        Document(page_content="three", metadata={}),
    ]).load(metadata_source_index="title")
    assert [row["url"] for row in rows] == ["Title", "fallback.md", ""]
