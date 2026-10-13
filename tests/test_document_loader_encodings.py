"""Read real encoded documents through the upstream document loaders."""
import asyncio

import pytest

from gpt_researcher.document.document import DocumentLoader

TEXT = "中文文档验收：Agent 工作流需要保存状态，检索结果需要引用来源。"


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "gbk"])
def test_text_encoding_preserves_content_and_source(tmp_path, encoding):
    path = tmp_path / "notes.txt"
    path.write_bytes(TEXT.encode(encoding))
    docs = asyncio.run(DocumentLoader([str(path)]).load())
    assert len(docs) == 1
    assert docs[0]["raw_content"] == TEXT
    assert docs[0]["url"] == "notes.txt"


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "gbk"])
def test_html_encoding_preserves_content_and_source(tmp_path, encoding):
    path = tmp_path / "notes.html"
    html = f'<html><head><meta charset="{encoding}"></head><body><p>{TEXT}</p></body></html>'
    path.write_bytes(html.encode(encoding))
    docs = asyncio.run(DocumentLoader([str(path)]).load())
    assert len(docs) == 1
    assert TEXT in docs[0]["raw_content"]
    assert docs[0]["url"] == "notes.html"
