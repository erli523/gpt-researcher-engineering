import asyncio
import os

from langchain_core.documents import Document
from typing import List, Dict


# Supports the base Document class from langchain
# - https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/documents/base.py
class LangChainDocumentLoader:

    def __init__(self, documents: List[Document]):
        self.documents = documents

    async def load(self, metadata_source_index="title") -> List[Dict[str, str]]:
        docs = []
        for document in self.documents:
            metadata = document.metadata or {}
            # LangChain's standard provenance key is ``source``.  The legacy
            # loader defaulted to ``title`` and silently erased provenance for
            # ordinary Documents that only provide source metadata.
            source = metadata.get(metadata_source_index) or metadata.get("source") or ""
            docs.append(
                {
                    "raw_content": document.page_content,
                    "url": source,
                }
            )
        return docs
