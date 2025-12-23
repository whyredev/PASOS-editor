import json
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QLineEdit, QComboBox, QSizePolicy
from . import utils

manim_rate_functions = [
    "linear", "smooth", "smoothstep", "rush_into",
    "rush_from", "slow_into", "double_smooth", "there_and_back",
    "there_and_back_with_pause", "running_start", "wiggle", "lingering",
    "exponential_decay", "ease_in_sine", "ease_out_sine", "ease_in_out_sine",
    "ease_in_quad", "ease_out_quad", "ease_in_out_quad", "ease_in_cubic",
    "ease_out_cubic", "ease_in_out_cubic", "ease_in_quart", "ease_out_quart",
    "ease_in_out_quart", "ease_in_quint", "ease_out_quint", "ease_in_out_quint",
    "ease_in_expo", "ease_out_expo", "ease_in_out_expo", "ease_in_circ",
    "ease_out_circ", "ease_in_out_circ", "ease_in_back", "ease_out_back",
    "ease_in_out_back", "ease_in_elastic", "ease_out_elastic", "ease_in_out_elastic",
    "ease_in_bounce", "ease_out_bounce", "ease_in_out_bounce", "ease_in_out_bounce"
]

sprite_classes = {}
with open("src/data/default_sprite_classes.json", "r") as f:
    sprite_classes.update(json.load(f))

class QHSeparationLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

class EventEditor(QWidget):
    cur_event = None

    def __init__(self):
        super().__init__()
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()
        self.setLayout(layout1)

        layout1.addLayout(layout2)
        layout1.addWidget(QHSeparationLine())

        start_label = QLabel("Start:")
        self.start_edit = QLineEdit()
        self.start_edit.textChanged.connect(lambda txt: self.change_event_value(0, txt))
        duration_label = QLabel("Duration:")
        self.duration_edit = QLineEdit()
        easing_label = QLabel("Easing:")
        self.easing_edit = QComboBox()
        self.easing_edit.addItems(manim_rate_functions)
        layout2.addWidget(start_label)
        layout2.addWidget(self.start_edit)
        layout2.addWidget(duration_label)
        layout2.addWidget(self.duration_edit)
        layout2.addWidget(easing_label)
        layout2.addWidget(self.easing_edit)
    
    def open_event(self, event):
        self.cur_event = event
        self.setDisabled(event == None)
        self.update_event_variables()

    def update_event_variables(self):
        if self.cur_event == None:
            self.start_edit.setText("")
            self.duration_edit.setText("")
            self.easing_edit.setCurrentIndex(0)
        else:
            self.start_edit.setText(str(self.cur_event[0]))
            self.duration_edit.setText(str(self.cur_event[1]))
            self.easing_edit.setCurrentText(str(self.cur_event[2]))
    
    def change_event_value(self):
        pass