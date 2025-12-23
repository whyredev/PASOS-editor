from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal

# before importing manim, we have to kill its logger than tqdm because otherwise the program crashes when trying to render scenes
import logging
logging.getLogger("manim").setLevel(logging.ERROR) # this kills manim's logger
import tqdm
setattr(tqdm.tqdm, "__init__", lambda self, iterable, *args, **kwargs: setattr(self, "iterable", iterable))
setattr(tqdm.tqdm, "__iter__", lambda self: iter(self.iterable))
setattr(tqdm.tqdm, "update", lambda self: None)
setattr(tqdm.tqdm, "close", lambda self: None) # these setattr functions kill manim's tqdm (tho this part might be dangerous because it might affect other libraries)
from .pasos import PASOS

class ExportDialog(QDialog):
    def __init__(self, scene, movie_path):
        super().__init__()
        self.scene = scene
        self.movie_path = movie_path
        self.setWindowTitle("Export Scene")
        
        layout1 = QVBoxLayout()
        self.setLayout(layout1)
        
        self.progress = QProgressBar()
        layout1.addWidget(self.progress)
        
        self.status = QLabel("Rendering...")
        layout1.addWidget(self.status)
        
        self.thread = ExportThread(self.scene, self.movie_path)
        self.thread.progress_callback.connect(lambda t: self.progress.setValue(int(t*100)))
        self.thread.finished.connect(self.exporting_finished)
        self.thread.start()

    def exporting_finished(self, output_path):
        self.status.setText(f"Done! Saved at:\n{output_path}")

class ExportThread(QThread):
    progress_callback = pyqtSignal(float)
    finished = pyqtSignal(str)

    def __init__(self, scene, movie_path):
        super().__init__()
        self.scene = scene
        self.movie_path = movie_path
        self.frames_rendered = 0
        self.n_of_frames = int(scene.duration * scene.camera.frame_rate)
    
    def patched_write_frame(self, *args, **kwargs):
        self.original_write_frame(*args, **kwargs)
        self.frames_rendered += 1
        progress_float = self.frames_rendered / self.n_of_frames
        self.progress_callback.emit(progress_float)

    def run(self):
        # a new scene is created for rendering so the editor's scene isn't modified
        export_scene = PASOS(True)
        export_scene.duration = self.scene.duration
        export_scene.timeline = self.scene.timeline
        export_scene.invisible_objects = self.scene.invisible_objects
        
        # monkey patch of FileWriter.write_frame
        fw = export_scene.renderer.file_writer
        self.original_write_frame = fw.write_frame
        fw.write_frame = self.patched_write_frame
        
        # rendering
        export_scene.renderer.file_writer.movie_file_path = self.movie_path
        export_scene.render(True)
        self.finished.emit(self.movie_path)
        self.deleteLater()