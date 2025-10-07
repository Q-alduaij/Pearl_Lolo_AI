import os
import time
from typing import List
from core.contracts import (
    Provider,
    Capability,
    Task,
    ProviderResult,
    Citation,
    Health,
    Usage,
)
from core.settings import load_settings
from core.logs import log
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

SETTINGS = load_settings()


class RagProvider(Provider):
    name = "rag"
    capabilities = [Capability.RAG]

    def __init__(self) -> None:
        directory = os.path.expanduser(SETTINGS.rag.persist_dir)
        os.makedirs(directory, exist_ok=True)
        self.client = chromadb.Client(chromadb.config.Settings(persist_directory=directory))
        if SETTINGS.rag.collection not in [c.name for c in self.client.list_collections()]:
            self.client.create_collection(SETTINGS.rag.collection)
        self.coll = self.client.get_collection(SETTINGS.rag.collection)
        self.embedder = embedding_functions.DefaultEmbeddingFunction()
        self._bm25 = None
        self._bm25_docs = None

    def _ensure_bm25(self) -> None:
        if self._bm25 is not None:
            return
        items = self.coll.get(include=["documents", "metadatas", "ids"])
        docs = items.get("documents", [])
        if not docs:
            self._bm25, self._bm25_docs = None, []
            return
        tokenised = [doc.split() for doc in docs]
        self._bm25 = BM25Okapi(tokenised)
        self._bm25_docs = list(zip(items["ids"], docs, items["metadatas"]))

    def health(self) -> Health:
        try:
            count = self.coll.count()
            return Health(name=self.name, ok=True, details={"count": count})
        except Exception as exc:  # noqa: BLE001
            return Health(name=self.name, ok=False, details={"error": str(exc)})

    def _dense(self, query: str, k: int) -> List[Citation]:
        result = self.coll.query(query_texts=[query], n_results=k)
        citations: List[Citation] = []
        for i, doc_id in enumerate(result["ids"][0]):
            citations.append(
                Citation(
                    source=result["metadatas"][0][i].get("source", doc_id),
                    snippet=result["documents"][0][i][:400],
                    score=float(result.get("distances", [[None]])[0][i])
                    if result.get("distances")
                    else None,
                )
            )
        return citations

    def _bm25_top(self, query: str, k: int) -> List[Citation]:
        self._ensure_bm25()
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(query.split())
        top = sorted([(score, idx) for idx, score in enumerate(scores)], reverse=True)[:k]
        citations: List[Citation] = []
        for score, idx in top:
            _id, doc, meta = self._bm25_docs[idx]
            citations.append(
                Citation(source=meta.get("source", _id), snippet=doc[:400], score=float(score))
            )
        return citations

    def invoke(self, task: Task) -> ProviderResult:
        start = time.time()
        query = task.messages[-1].content
        k = int(task.params.get("k", SETTINGS.rag.k))
        dense = self._dense(query, k)
        bm25 = (
            self._bm25_top(query, k)
            if self.coll.count() >= SETTINGS.rag.bm25_min_docs
            else []
        )
        seen = {}
        for citation in bm25 + dense:
            key = (citation.source, citation.snippet[:120])
            if key not in seen:
                seen[key] = citation
        citations = list(seen.values())[:k]
        compose = bool(task.params.get("compose", True))
        if compose:
            if citations:
                text = "Here are relevant passages:\n" + "\n".join(
                    f"- {c.source}: {c.snippet}" for c in citations
                )
            else:
                text = "Insufficient evidence. Here are sources to consult (index may be small)."
        else:
            text = ""
        usage = Usage(latency_ms=int((time.time() - start) * 1000))
        log(
            "rag.invoke",
            k=k,
            dense=len(dense),
            bm25=len(bm25),
            fused=len(citations),
            latency_ms=usage.latency_ms,
        )
        return ProviderResult(ok=True, text=text, citations=citations, usage=usage)
