import sys
from PyQt6.QtWidgets import QApplication

from src.pasos import PASOS
from src.preview import run_preview_window
from src.editor import EditorWindow

preview = PASOS(False)
app = QApplication(sys.argv)
EditorWindow(preview).show()
sys.exit(app.exec())