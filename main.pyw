import sys
import threading
from PyQt6.QtWidgets import QApplication

from src.pasos import PASOS
from src.preview import run_preview_window
from src.editor import EditorWindow

preview = PASOS(False)
t1 = threading.Thread(target=run_preview_window, args=(preview,))
app = QApplication(sys.argv)
EditorWindow(preview).show()
t1.start()
sys.exit(app.exec())