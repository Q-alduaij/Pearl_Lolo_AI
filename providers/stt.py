from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage


class SttProvider(Provider):
    name = "stt"
    capabilities = [Capability.STT]

    def health(self) -> Health:
        return Health(name=self.name, ok=True, details={"impl": "stub"})

    def invoke(self, task: Task) -> ProviderResult:  # noqa: ARG002
        return ProviderResult(
            ok=True,
            text="(STT stub — install faster-whisper to transcribe.)",
            usage=Usage(),
        )
