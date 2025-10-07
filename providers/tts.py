from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage


class TtsProvider(Provider):
    name = "tts"
    capabilities = [Capability.TTS]

    def health(self) -> Health:
        return Health(name=self.name, ok=True, details={"impl": "stub"})

    def invoke(self, task: Task) -> ProviderResult:  # noqa: ARG002
        return ProviderResult(
            ok=True,
            text="(TTS stub — install piper-tts to synthesize.)",
            usage=Usage(),
        )
