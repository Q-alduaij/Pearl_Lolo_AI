from providers.rag import RagProvider
from core.contracts import Task, Message, Capability


def test_rag_health() -> None:
    provider = RagProvider()
    health = provider.health()
    assert health.name == "rag"


def test_rag_invoke_empty_index_ok() -> None:
    provider = RagProvider()
    task = Task(intent=Capability.RAG, messages=[Message(role="user", content="Kuwait Vision")])
    result = provider.invoke(task)
    assert result.ok
