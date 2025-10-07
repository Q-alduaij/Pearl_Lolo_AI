import subprocess
import sys
from core.settings import load_settings

settings = load_settings()


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd)


print("Checking Ollama …")
rc = run(["curl", "-s", f"{settings.llm.url}/api/tags"])
if rc != 0:
    print("Ollama not reachable. Install from https://ollama.com and run `ollama serve`.")
    sys.exit(1)
for model in (settings.llm.primary_model, settings.llm.fallback_model):
    print(f"Ensuring model: {model}")
    run(["ollama", "pull", model])
