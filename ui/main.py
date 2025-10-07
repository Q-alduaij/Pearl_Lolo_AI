import threading
import sys
import httpx
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QMessageBox,
)
from ui.widgets import TEMPLATES, SettingsDialog

API = "http://127.0.0.1:8777"


def _post_invoke(payload: dict) -> dict:
    with httpx.Client(timeout=60.0) as client:
        response = client.post(f"{API}/invoke", json=payload)
        response.raise_for_status()
        return response.json()


class Main(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LoLo — Local Aide")
        self.resize(900, 600)
        self.template = QComboBox()
        for name in TEMPLATES.keys():
            self.template.addItem(name)
        self.intent = QComboBox()
        for item in ["chat", "rag", "solve", "stt", "tts", "search"]:
            self.intent.addItem(item)
        self.inp = QTextEdit()
        self.inp.setPlaceholderText("Type your prompt here …")
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        run = QPushButton("Run")
        run.clicked.connect(self.run_task)
        settings = QPushButton("Settings")
        settings.clicked.connect(self.open_settings)
        top = QHBoxLayout()
        top.addWidget(QLabel("Template:"))
        top.addWidget(self.template)
        top.addWidget(QLabel("Intent:"))
        top.addWidget(self.intent)
        top.addWidget(settings)
        top.addWidget(run)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(QLabel("Input"))
        layout.addWidget(self.inp, 2)
        layout.addWidget(QLabel("Output"))
        layout.addWidget(self.out, 3)
        self.template.currentTextChanged.connect(self.apply_template)
        self.apply_template(self.template.currentText())

    def apply_template(self, name: str) -> None:
        template = TEMPLATES[name]
        self.intent.setCurrentText(template.get("intent", "chat"))
        self.inp.setPlainText(template.get("prefix", ""))

    def open_settings(self) -> None:
        dialog = SettingsDialog(self, values={})
        if dialog.exec():
            QMessageBox.information(self, "Info", "Settings saved (restart may be needed).")

    def run_task(self) -> None:
        intent = self.intent.currentText()
        text = self.inp.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Enter prompt text.")
            return
        payload = {
            "intent": intent,
            "messages": [{"role": "user", "content": text}],
            "params": {},
            "attachments": [],
            "locale": "en-GB",
            "tz": "Asia/Kuwait",
            "user_tags": [],
        }
        self.out.setPlainText("Running…")

        def worker() -> None:
            try:
                result = _post_invoke(payload)
                output_text = result.get("text", "")
                citations = result.get("citations", [])
                if citations:
                    output_text += "\n\n---\nCitations:\n" + "\n".join(
                        f"- {citation.get('source', '')}: {citation.get('snippet', '')[:140]}"
                        for citation in citations
                    )
                self.out.setPlainText(output_text)
            except Exception as exc:  # noqa: BLE001
                self.out.setPlainText(f"Error: {exc}")

        threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    app = QApplication(sys.argv)
    widget = Main()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
