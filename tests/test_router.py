from core.router import Router
from core.contracts import Capability, Task, Message, ProviderResult, Provider, Health


class Dummy(Provider):
    name = "dummy"
    capabilities = [Capability.CHAT]

    def health(self) -> Health:
        return Health(name=self.name, ok=True, details={})

    def invoke(self, task: Task) -> ProviderResult:  # noqa: ARG002
        return ProviderResult(ok=True, text="ok")


def test_router_default() -> None:
    router = Router({Capability.CHAT: Dummy()})
    result = router.route(Task(intent=Capability.CHAT, messages=[Message(role="user", content="hi")]))
    assert result.ok and result.text == "ok"
