from __future__ import annotations
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
import yaml

APP_HOME = Path(os.getenv("LOLO_HOME", Path.home() / ".lolo"))


class LlmCfg(BaseModel):
    url: str = "http://127.0.0.1:11434"
    primary_model: str = "qwen2.5:14b"
    fallback_model: str = "qwen2.5:7b"
    timeout_s: float = 60.0


class RagCfg(BaseModel):
    persist_dir: str = str(APP_HOME / "rag")
    collection: str = "main"
    k: int = 5
    bm25_min_docs: int = 20


class HrmCfg(BaseModel):
    url: str = "http://127.0.0.1:8008"
    health_path: str = "/health"
    solve_path: str = "/solve"
    timeout_s: float = 20.0
    enforce_fenced_block: bool = False


class ApiCfg(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8777


class SearchCfg(BaseModel):
    enabled: bool = False
    provider: str = "tavily"
    max_results: int = 5
    timeout_s: float = 12.0


class LlmModeCfg(BaseModel):
    mode: str = "local"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOLO_", env_file=".env.local", extra="ignore")
    home: str = str(APP_HOME)
    api: ApiCfg = ApiCfg()
    llm: LlmCfg = LlmCfg()
    rag: RagCfg = RagCfg()
    hrm: HrmCfg = HrmCfg()
    search: SearchCfg = SearchCfg()
    llm_mode: LlmModeCfg = LlmModeCfg()

    def __init__(self, **data):
        super().__init__(**data)
        Path(self.home).mkdir(parents=True, exist_ok=True)
        Path(self.home, "logs").mkdir(parents=True, exist_ok=True)


def load_settings() -> AppSettings:
    base = AppSettings()
    yaml_path = Path("config/config.yaml")
    if yaml_path.exists():
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if "llm" in data:
            base.llm = LlmCfg(**{**base.llm.model_dump(), **data["llm"]})
        if "rag" in data:
            base.rag = RagCfg(**{**base.rag.model_dump(), **data["rag"]})
        if "hrm" in data:
            base.hrm = HrmCfg(**{**base.hrm.model_dump(), **data["hrm"]})
        if "api" in data:
            base.api = ApiCfg(**{**base.api.model_dump(), **data["api"]})
        if "search" in data:
            base.search = SearchCfg(**{**base.search.model_dump(), **data["search"]})
        if "llm_mode" in data:
            base.llm_mode = LlmModeCfg(**{**base.llm_mode.model_dump(), **data["llm_mode"]})
    return base
