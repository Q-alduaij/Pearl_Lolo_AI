from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDialogButtonBox,
)

TEMPLATES = {
    "Script Builder (CHAT)": {
        "intent": "chat",
        "prefix": "أنت منتج إذاعي محترف. اصنع فقرة إذاعية موجزة:\n",
    },
    "Brief w/ Sources (RAG)": {
        "intent": "rag",
        "params": {"k": 5, "compose": True},
        "prefix": "Provide a concise, source-backed brief:\n",
    },
    "Fact-check (RAG)": {
        "intent": "rag",
        "params": {"k": 7, "compose": True},
        "prefix": "Fact-check the following claim. Cite sources:\n",
    },
    "HRM Planner": {
        "intent": "solve",
        "params": {"hrm_task": "plan"},
        "prefix": (
            "Break down this request into actionable steps, call out assumptions, and propose "
            "what to execute next:\n\n- Objective: Improve LoLo onboarding\n- Constraints: keep offline-first"
        ),
    },
}

TEMPLATES.update(
    {
        "Web Search (NET)": {
            "intent": "search",
            "prefix": "net: Kuwait housing policy 2024 site:un.org",
        }
    }
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, values=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        values = values or {}
        form = QFormLayout(self)
        self.llm_url = QLineEdit(values.get("llm_url", "http://127.0.0.1:11434"))
        self.llm_primary = QLineEdit(values.get("llm_primary", "qwen2.5:14b"))
        self.llm_fallback = QLineEdit(values.get("llm_fallback", "qwen2.5:7b"))
        self.rag_k = QSpinBox()
        self.rag_k.setRange(1, 50)
        self.rag_k.setValue(values.get("rag_k", 5))
        self.hrm_url = QLineEdit(values.get("hrm_url", "http://127.0.0.1:8008"))
        form.addRow("LLM URL", self.llm_url)
        form.addRow("LLM Primary", self.llm_primary)
        form.addRow("LLM Fallback", self.llm_fallback)
        form.addRow("RAG k", self.rag_k)
        form.addRow("HRM URL", self.hrm_url)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def values(self):
        return {
            "llm_url": self.llm_url.text(),
            "llm_primary": self.llm_primary.text(),
            "llm_fallback": self.llm_fallback.text(),
            "rag_k": self.rag_k.value(),
            "hrm_url": self.hrm_url.text(),
        }
