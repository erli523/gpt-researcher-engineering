"""Real upstream multi-agent publishing catches export regressions."""
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from multi_agents.agents.publisher import PublisherAgent
from multi_agents.agents.utils.file_formats import write_md_to_pdf


@pytest.mark.asyncio
async def test_pdf_export_uses_installed_md2pdf_api(tmp_path, monkeypatch):
    calls = []
    def converted(pdf, raw=None, css=None, base_url=None):
        calls.append((pdf, raw, css, base_url))
        pdf.write_bytes(b"%PDF-1.7\nfixture")
    import md2pdf.core
    monkeypatch.setattr(md2pdf.core, "md2pdf", converted)
    path = await write_md_to_pdf("# Public test", str(tmp_path))
    assert path and calls
    assert calls[0][0].is_file()
    assert calls[0][1] == "# Public test"
    assert calls[0][2].name == "pdf_styles.css"


@pytest.mark.asyncio
async def test_publisher_reports_requested_pdf_failure(tmp_path, monkeypatch):
    import multi_agents.agents.publisher as module
    monkeypatch.setattr(module, "write_md_to_pdf", AsyncMock(return_value=""))
    publisher = PublisherAgent(str(tmp_path))
    with pytest.raises(RuntimeError, match="PDF report"):
        await publisher.write_report_by_formats("# Public test", {"pdf": True, "markdown": True})
