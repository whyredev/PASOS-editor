from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFontMetrics, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QRect

def qcolor_interpolation(color1: QColor, color2: QColor, alpha: float) -> QColor:
    if alpha < 0 or alpha > 1:
        raise ValueError("alpha must be a number between between 0 and 1")

    r1, g1, b1, a1 = color1.getRgb()
    r2, g2, b2, a2 = color2.getRgb()

    new_r = int(r1 + (r2 - r1) * alpha)
    new_g = int(g1 + (g2 - g1) * alpha)
    new_b = int(b1 + (b2 - b1) * alpha)
    new_a = int(a1 + (a2 - a1) * alpha)

    return QColor(new_r, new_g, new_b, new_a)

class TimeLineCanvas(QWidget):
    edit_event = pyqtSignal(object)
    timeline_changed = pyqtSignal()
    sec_width = 60 # width of a second
    row_height = 20
    hovered_row_idx = 0
    hovered_row = None
    hovered_event_idx = 0
    hovered_event = None
    left_barrier = 0
    right_barrier = 0
    resizing_side = None
    resizing_flag = False
    resizing_end = 0
    selected_events = set()
    selected_events_mapping = {}
    moving_flag = False
    moving_offset = 0

    def __init__(self, scene, scroll_area):
        super().__init__()
        self.scene = scene
        self.scroll_area = scroll_area
        self.setMouseTracking(True)
        self.update_size()

        palette = self.style().standardPalette() # get the OS palette
        self.bg_color = qcolor_interpolation(palette.color(QPalette.ColorRole.Button), palette.color(QPalette.ColorRole.Dark), 0.75)
        self.row_fill = palette.color(QPalette.ColorRole.Button)
        self.grid_color = qcolor_interpolation(palette.color(QPalette.ColorRole.Button), palette.color(QPalette.ColorRole.Dark), 0.5)
        self.row_label_border = qcolor_interpolation(palette.color(QPalette.ColorRole.Dark), palette.color(QPalette.ColorRole.Text), 0.25)
        self.row_label_fill = qcolor_interpolation(palette.color(QPalette.ColorRole.Button), palette.color(QPalette.ColorRole.Dark), 0.25)
        self.event_border = qcolor_interpolation(QColor("#000000"), QColor("#FC6255"), 0.75)
        self.event_fill = qcolor_interpolation(palette.color(QPalette.ColorRole.Button), QColor("#FC6255"), 0.5)
        self.selected_event_border = qcolor_interpolation(QColor("#000000"), QColor("#FFFF00"), 0.75)
        self.selected_event_fill = qcolor_interpolation(palette.color(QPalette.ColorRole.Button), QColor("#FFFF00"), 0.5)
        self.cursor_color = palette.color(QPalette.ColorRole.Text)
    
    def update_size(self):
        self.n_of_rows = len(self.scene.timeline) + 5 # how many rows will be displayed
        self.duration_width = 100 + int(self.scene.duration * self.sec_width)
        row_accumulated_height = self.n_of_rows * self.row_height
        self.setMinimumSize(max(self.duration_width, self.scroll_area.width()), max(row_accumulated_height, self.scroll_area.height()))

    def paintEvent(self, event):
        self.update_size()

        painter = QPainter(self)
        font = self.font()
        painter.setFont(font)
        
        # draw background
        painter.setBrush(self.bg_color)
        painter.fillRect(0, 0, self.width(), self.height(), painter.brush())

        # draw rows
        painter.setPen(self.grid_color)
        painter.setBrush(self.grid_color)
        painter.fillRect(100, 0, self.width(), self.n_of_rows * self.row_height, painter.brush())
        painter.setBrush(self.row_fill)
        painter.fillRect(100, 0, self.duration_width - 100, self.n_of_rows * self.row_height, painter.brush())
        for row in range(1, self.n_of_rows + 1): # draw grid
            painter.drawLine(100, row * self.row_height, self.width(), row * self.row_height)
        
        # draw row labels
        painter.setPen(self.row_label_border)
        painter.setBrush(self.row_label_fill)
        painter.fillRect(0, 0, 100, self.n_of_rows * self.row_height, painter.brush())
        for row in range(self.n_of_rows):
            rect_text = "mob" + str(row//5 + 1) + "." + ["position", "angle", "scale", "opacity", "sprite"][row%5]
            painter.drawRect(0, row * self.row_height, 100, self.row_height)
            painter.drawText(
                QRect(5, row * self.row_height, 90, self.row_height),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                QFontMetrics(font).elidedText(rect_text, Qt.TextElideMode.ElideRight, 90)
                )
        
        # draw events
        for row_idx, row in enumerate(self.scene.timeline):
            for p_event in row: #p_event stands for "pasos event"
                if id(p_event) in self.selected_events:
                    painter.setPen(self.selected_event_border)
                    painter.setBrush(self.selected_event_fill)
                else:
                    painter.setPen(self.event_border)
                    painter.setBrush(self.event_fill)
                rect = QRect(100 + int(p_event[0] * self.sec_width), row_idx * self.row_height, int(p_event[1] * self.sec_width), self.row_height)
                painter.fillRect(rect, painter.brush())
                painter.drawRect(rect)
                painter.drawText(
                    QRect(rect.x() + 5, row_idx * self.row_height, rect.width() - 10, self.row_height),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    QFontMetrics(font).elidedText(p_event[3], Qt.ElideRight, 90)
                    )
        
        # draw cursor
        painter.setPen(self.cursor_color)
        time_x = 100 + int(self.scene.edtv["time"] * self.sec_width)
        painter.drawLine(time_x, 0, time_x, self.height())
        
        painter.end()

    def mouseMoveEvent(self, event):
        mouse_time = (event.position().x() - 100) / self.sec_width
        
        if self.resizing_flag:
            if self.resizing_side == "left":
                new_start = min(max(mouse_time, self.left_barrier),  self.right_barrier)
                self.hovered_event[0] = new_start
                self.hovered_event[1] = self.resizing_end - new_start
            elif self.resizing_side == "right":
                self.hovered_event[1] = min(max(mouse_time, self.left_barrier),  self.right_barrier) - self.hovered_event[0]
            self.timeline_changed.emit()
            self.update()
            return

        if self.moving_flag:
            for p_event_id in self.selected_events:
                p_event = self.selected_events_mapping[p_event_id]
                p_event[0] = mouse_time + self.moving_offset
                self.timeline_changed.emit()
                self.update()

        if self.hovered_row_idx != (new_row_idx := event.position().y() // self.row_height):
            self.hovered_row_idx = new_row_idx
            self.hovered_row = None
            self.hovered_event = None
            self.left_barrier = 0
            self.right_barrier = self.scene.duration
            if 0 <= new_row_idx < len(self.scene.timeline):
                self.hovered_row = self.scene.timeline[new_row_idx]
        
        if mouse_time < self.scene.duration and self.hovered_row and not (self.hovered_event and self.hovered_event[0] < mouse_time < self.hovered_event[0] + self.hovered_event[1]):
            self.hovered_event_idx, self.hovered_event = next(((i,e) for i, e in enumerate(self.hovered_row) if e[0] < mouse_time < e[0] + e[1]), (0, None))

        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.resizing_side = None
        if not self.hovered_event:
            return

        e_start = self.hovered_event[0]
        e_end = e_start + self.hovered_event[1]
        if mouse_time < e_start + 10/self.sec_width:
            self.setCursor(Qt.SizeHorCursor)
            self.resizing_side = "left"
            if self.hovered_event_idx > 0:
                previous_event = self.hovered_row[self.hovered_event_idx - 1]
                self.left_barrier = previous_event[0] + previous_event[1]
            else:
                self.left_barrier = 0
            self.right_barrier = e_end
            self.resizing_end = e_end
        if mouse_time > e_end - 10/self.sec_width:
            self.setCursor(Qt.SizeHorCursor)
            self.resizing_side = "right"
            self.left_barrier = e_start
            self.right_barrier = self.hovered_row[self.hovered_event_idx + 1][0] if self.hovered_event_idx < len(self.hovered_row) - 1 else self.scene.duration

    def mousePressEvent(self, event):
        if self.resizing_side:
            self.resizing_flag = True
            return
        
        self.selected_events.clear()
        self.selected_events_mapping.clear()
        if self.hovered_event:
            self.selected_events.add(id(self.hovered_event))
            self.selected_events_mapping[id(self.hovered_event)] = self.hovered_event
            self.edit_event.emit(self.hovered_event)
            self.moving_flag = True
            self.moving_offset = self.hovered_event[0] - (event.position().x() - 100) / self.sec_width
            self.update()
            return
        
        self.edit_event.emit(None)
        self.update()

    def mouseReleaseEvent(self, event):
        self.resizing_flag = False
        self.moving_flag = False
        self.mouseMoveEvent(event)