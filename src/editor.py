import os
import json
import math
from PyQt6.QtWidgets import (QMainWindow, QWidget, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QGroupBox, QScrollArea, QLabel, QLineEdit, QSlider, QPushButton, QStyle, QSizePolicy)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from .export import ExportDialog
from .timeline_editor import TimeLineCanvas
from .event_editor import EventEditor

def create_menubar(window, menubar):
    file_menu = menubar.addMenu("File")
    file_menu_action = file_menu.addAction("New")
    file_menu_action.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    file_menu_action.setShortcut("Ctrl+N")
    file_menu_action.triggered.connect(lambda: window.unsaved_changes_message(window.new_file))
    file_menu_action = file_menu.addAction("Open")
    file_menu_action.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
    file_menu_action.setShortcut("Ctrl+O")
    file_menu_action.triggered.connect(lambda: window.unsaved_changes_message(window.open_file))
    file_menu_action = file_menu.addAction("Save")
    file_menu_action.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
    file_menu_action.setShortcut("Ctrl+S")
    file_menu_action.triggered.connect(window.save_file)
    file_menu_action = file_menu.addAction("Save As...")
    file_menu_action.setShortcut("Ctrl+Alt+S")
    file_menu_action.triggered.connect(window.save_file_as)
    file_menu_action = file_menu.addAction("Export")
    file_menu_action.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon))
    file_menu_action.setShortcut("Ctrl+E")
    file_menu_action.triggered.connect(window.export_scene)

def create_time_edit(window, layout1):
    window.time_edit = QSlider(Qt.Orientation.Horizontal)
    window.time_edit.valueChanged.connect(window.time_slider_moved)
    layout1.addWidget(window.time_edit)

def create_duration_edit(window, layout2):
    duration_label = QLabel("Duration (seconds):")
    duration_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    window.duration_edit = QLineEdit(text=str(window.scene.duration))
    window.duration_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    window.duration_edit.setMinimumWidth(0)
    window.duration_edit.textChanged.connect(window.duration_changed)
    layout2.addWidget(duration_label)
    layout2.addWidget(window.duration_edit)

def create_media_buttons(window, layout2):
    mbtn_back = QPushButton()
    mbtn_back.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
    mbtn_back.clicked.connect(lambda: window.set_time_to(max(window.scene.edtv["time"] - window.scene.edtv["scroll_speed"], 0)))
    window.mbtn_play = QPushButton()
    window.mbtn_play.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    window.mbtn_play.clicked.connect(window.playing_toggle)
    mbtn_forward = QPushButton()
    mbtn_forward.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
    mbtn_forward.clicked.connect(lambda: window.set_time_to(min(window.scene.edtv["time"] + window.scene.edtv["scroll_speed"], window.scene.duration)))
    layout2.addWidget(mbtn_back)
    layout2.addWidget(window.mbtn_play)
    layout2.addWidget(mbtn_forward)

    playing_speed_label = QLabel("Playing speed:")
    playing_speed_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    playing_speed_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    playing_speed_edit = QLineEdit(text=str(window.scene.edtv["playing_speed"]))
    playing_speed_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    playing_speed_edit.setMinimumWidth(0)
    playing_speed_edit.textChanged.connect(lambda x: window.float_var_el_changed("playing_speed", x))
    scroll_speed_label = QLabel("Scroll speed:")
    scroll_speed_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    scroll_speed_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    scroll_speed_edit = QLineEdit(text=str(window.scene.edtv["scroll_speed"]))
    scroll_speed_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    scroll_speed_edit.setMinimumWidth(0)
    scroll_speed_edit.textChanged.connect(lambda x: window.float_var_el_changed("scroll_speed", x))
    layout2.addWidget(playing_speed_label)
    layout2.addWidget(playing_speed_edit)
    layout2.addWidget(scroll_speed_label)
    layout2.addWidget(scroll_speed_edit)

def create_time_displayer(window, layout2):
    window.time_displayer = QLabel("Time: 0.00s")
    window.time_displayer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    window.time_displayer.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    layout2.addWidget(window.time_displayer)

def create_timeline_edit(window, layout1, layout3):
    window.timeline_edit = QScrollArea()
    window.timeline_canvas = TimeLineCanvas(window.scene, window.timeline_edit)
    window.timeline_canvas.timeline_changed.connect(lambda: window.update_unsaved_changes_flag(True))
    window.timeline_edit.setWidget(window.timeline_canvas)
    window.timeline_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    window.timeline_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    layout1.addWidget(window.timeline_edit)
    layout1.addLayout(layout3)
    
    secwidth_label = QLabel("Width of a second (pixels):")
    secwidth_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    secwidth_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    secwidth_edit = QLineEdit(text=str(window.scene.edtv["timeline_sec_width"]))
    secwidth_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    secwidth_edit.setMinimumWidth(0)
    secwidth_edit.textChanged.connect(lambda x: window.float_var_el_changed("timeline_sec_width", x, "positive_int"))
    timeline_zoom_out = QPushButton("-")
    timeline_zoom_out.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    timeline_zoom_out.setMinimumWidth(0)
    timeline_zoom_out.clicked.connect(lambda: window.set_float_var("timeline_sec_width", math.ceil(window.scene.edtv["timeline_sec_width"] / 1.25), secwidth_edit))
    timeline_zoom_in = QPushButton("+")
    timeline_zoom_in.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    timeline_zoom_in.setMinimumWidth(0)
    timeline_zoom_in.clicked.connect(lambda: window.set_float_var("timeline_sec_width", int(window.scene.edtv["timeline_sec_width"] * 1.25), secwidth_edit))
    layout3.addWidget(secwidth_label)
    layout3.addWidget(secwidth_edit)
    layout3.addWidget(timeline_zoom_out)
    layout3.addWidget(timeline_zoom_in)

def create_event_edit(window, layout1):
    event_editor_box = QGroupBox("Event editor")
    event_editor_box.setStyleSheet("""
        QGroupBox {
        border: 1px solid palette(mid);
        margin-top: 6px;
        }

        QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
        }
    """)
    window.event_editor_widget = EventEditor()
    window.event_editor_widget.open_event(None)
    window.timeline_canvas.edit_event.connect(window.event_editor_widget.open_event)
    window.timeline_canvas.timeline_changed.connect(window.event_editor_widget.update_event_variables)
    temp = QVBoxLayout()
    temp.addWidget(window.event_editor_widget)
    event_editor_box.setLayout(temp)
    layout1.addWidget(event_editor_box)

class EditorWindow(QMainWindow):
    current_filepath = "untitled"
    updating_time_slider = False

    def update_unsaved_changes_flag(self, value):
        self.unsaved_changes = value
        self.setWindowTitle("*" * int(self.unsaved_changes) + os.path.basename(self.current_filepath) + " - PASOS Editor")

    def __init__(self, scene):
        super().__init__()
        
        self.scene = scene
        scene.construct()
        scene.edtv = {"function_call": [], "time": 0, "playing_speed": 1, "scroll_speed": 0.1, "playing": False, "timeline_sec_width": 60}
        # function_call is a list made to pass signals between pygame and pyqt. for example, when pyqt is closed, it appends "quit" to function_call (line 400), then pygame reads that (line 178) and stops running

        self.scene.edtv["editor_window_object"] = self
        self.scene.edtv["function_call"].append(self)
        self.scene.edtv["function_call"].append("update_pygame_editor_window_variable")
        self.update_unsaved_changes_flag(False)
        self.setWindowIcon(QIcon("icon_light.png"))
        self.resize(640, 480)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        central_widget.setLayout(layout1)

        menubar = self.menuBar()
        create_menubar(self, menubar)

        create_time_edit(self, layout1)
        layout1.addLayout(layout2)
        create_duration_edit(self, layout2)
        create_media_buttons(self, layout2)
        create_time_displayer(self, layout2)
        create_timeline_edit(self, layout1, layout3)
        create_event_edit(self, layout1)

        for row, size in enumerate([1, 1, 4, 1, 5]):
            layout1.setStretch(row, size)
        for column, size in enumerate([8, 3, 2, 2, 2, 6, 2, 6, 3, 9]):
            layout2.setStretch(column, size)
        for column, size in enumerate([70, 5, 1, 1]):
            layout3.setStretch(column, size)

    # file menu functions
    def new_file(self):
        self.scene.duration = 1
        self.scene.timeline = []
        self.scene.invisible_objects = []
        self.duration_edit.setText(str(self.scene.duration))
        self.timeline_canvas.update()
        self.set_time_to(0)
        self.scene.update_visible_mobs()
        self.current_filepath = "untitled"
        self.update_unsaved_changes_flag(False)
    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, caption="Open File", directory="", filter="JSON Files (*.json)")
        if filepath == "":
            return
        with open(filepath, "r") as f:
            file_dict = json.load(f)
            self.scene.duration = file_dict["duration"]
            self.scene.timeline = file_dict["timeline"]
            self.scene.invisible_objects = file_dict["invisible_objects"]
        self.duration_edit.setText(str(self.scene.duration))
        self.timeline_canvas.update()
        self.set_time_to(0)
        self.scene.update_visible_mobs()
        self.current_filepath = filepath
        self.update_unsaved_changes_flag(False)
    def save_file(self):
        self.save_file_as(self.current_filepath)
    def save_file_as(self, filepath):
        if filepath == "untitled" or isinstance(filepath, bool):
            filepath, _ = QFileDialog.getSaveFileName(self, caption="Save As", directory="", filter="JSON Files (*.json)")
            if filepath == "":
                return
        with open(filepath, "w") as f:
            file_dict = {
                "duration": self.scene.duration,
                "timeline": self.scene.timeline,
                "invisible_objects": self.scene.invisible_objects
                }
            json.dump(file_dict, f, indent=4)
        self.current_filepath = filepath
        self.update_unsaved_changes_flag(False)
    def export_scene(self):
        movie_path, _ = QFileDialog.getSaveFileName(self, caption="Export As", directory="", filter="MPEG4 (*.mp4);; MOV (*.mov);; GIF (*.gif)")
        if movie_path == "":
            return
        ExportDialog(self.scene, movie_path).exec_()
    
    def unsaved_changes_message(self, action):
        msg = QMessageBox()
        msg.setWindowTitle("Unsaved changes")
        msg.setText("Want to save your changes?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if self.unsaved_changes:
            answer = msg.exec_()
            msg.raise_()
            if answer == QMessageBox.Yes:
                self.save_file()
            if answer != QMessageBox.Cancel:
                action()
            return answer
        else:
            action()

    def set_time_to(self, t):
        self.scene.edtv["time"] = t
        self.updating_time_slider = True
        self.time_edit.setValue(int(100 * self.scene.edtv["time"] / self.scene.duration))
        self.time_displayer.setText(f'Time: {self.scene.edtv["time"]:.2f}s')
        self.timeline_canvas.update()
    def time_slider_moved(self, value):
        if self.updating_time_slider:
            self.updating_time_slider = False
        else:
            self.set_time_to(self.scene.duration * value / 100)

    def float_var_el_changed(self, variable, value, domain="positive"):
        try:
            new_value = float(value)
            if domain == "positive" and new_value <= 0:
                return
            elif domain == "positive_int" and new_value <= 0:
                new_value = round(new_value)
            self.set_float_var(variable, new_value)
        except Exception as e:
            print(e)
    def set_float_var(self, variable, value, edit_line=None):
        self.scene.edtv[variable] = value
        if variable == "timeline_sec_width":
            self.timeline_canvas.sec_width = value
            self.timeline_canvas.update()
        if edit_line != None:
            edit_line.setText(str(value))
    
    def duration_changed(self, value):
        try:
            new_duration = float(value)
            if new_duration <= 0:
                return
            self.scene.duration = new_duration
            self.set_time_to(min(self.scene.edtv["time"], new_duration))
            if self.timeline_canvas.hovered_event and new_duration < self.timeline_canvas.hovered_event[0]:
                self.timeline_canvas.hovered_event = None
                self.timeline_canvas.selected_events.clear()
                self.timeline_canvas.selected_events_mapping.clear()
                self.timeline_canvas.resizing_side = None
                self.timeline_canvas.resizing_flag = False
            self.timeline_canvas.update()
            self.update_unsaved_changes_flag(True)
        except Exception as e:
            print(e)

    def playing_toggle(self):
        if self.scene.edtv["playing"]:
            self.scene.edtv["playing"] = False
            self.mbtn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.scene.edtv["playing"] = True
            self.mbtn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
            self.scene.edtv["function_call"].append("start_playing")

    def closeEvent(self, event):
        answer = self.unsaved_changes_message(lambda: self.scene.edtv["function_call"].append("quit"))
        if answer == QMessageBox.Cancel:
            event.ignore()