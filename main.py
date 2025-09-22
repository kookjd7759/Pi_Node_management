from __future__ import annotations
import sys, os, time
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from path import *

ICON_SIZE = 48
CHECK_INTERVAL = 30  # seconds

class TimerPill(QtWidgets.QWidget):
    def __init__(self, total:int, min_w:int=86, h:int=28):
        super().__init__()
        self._total = max(1, int(total))
        self._remain = int(total)
        self.setMinimumWidth(min_w)
        self.setFixedHeight(h)
        self._font = QtGui.QFont()
        self._font.setPointSize(12)
        # soft shadow for a more polished look
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def set_total(self, total:int):
        self._total = max(1, int(total)); self.update()

    def set_remaining(self, remain:int):
        self._remain = max(0, int(remain)); self.update()

    def _fmt(self) -> str:
        m, s = divmod(self._remain, 60)
        return f"{m:02d}:{s:02d}"

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        # base pill
        base = QtGui.QColor(40, 42, 50, 230)
        p.setPen(Qt.NoPen)
        p.setBrush(base)
        radius = rect.height() / 2
        p.drawRoundedRect(rect, radius, radius)

        # progress fill (left -> right)
        frac = 1.0 - (self._remain / float(self._total))
        if frac > 0:
            prog = QtCore.QRectF(rect)
            prog.setWidth(rect.width() * min(1.0, max(0.0, frac)))
            grad = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
            grad.setColorAt(0.0, QtGui.QColor(60, 130, 255, 120))
            grad.setColorAt(1.0, QtGui.QColor(90, 200, 255, 120))
            p.setBrush(grad)
            p.drawRoundedRect(prog, radius, radius)

        # subtle border
        p.setBrush(Qt.NoBrush)
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 28), 1))
        p.drawRoundedRect(rect, radius, radius)

        # label
        p.setFont(self._font)
        p.setPen(QtGui.QColor(230, 232, 238))
        p.drawText(rect, Qt.AlignCenter, self._fmt())


class StatusWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: rgba(30,30,38,230); border-radius: 12px;")

        # layout: icon | status dot | timer label
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(12)

        # icon
        self.icon_label = QtWidgets.QLabel()
        if os.path.exists(ICON):
            pix = QtGui.QPixmap(ICON).scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pix)
        lay.addWidget(self.icon_label)

        # status dot
        self.status_dot = QtWidgets.QLabel()
        self.status_dot.setFixedSize(20, 20)
        self._set_status(True)
        lay.addWidget(self.status_dot)

        # timer pill (pretty background + progress)
        self.timer_pill = TimerPill(CHECK_INTERVAL)
        lay.addWidget(self.timer_pill)

        # logic
        self.remaining = CHECK_INTERVAL
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _set_status(self, ok: bool):
        pm = QtGui.QPixmap(20,20)
        pm.fill(Qt.transparent)
        qp = QtGui.QPainter(pm)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        qp.setBrush(QtGui.QColor(72,201,115) if ok else QtGui.QColor(231,76,60))
        qp.setPen(Qt.NoPen)
        qp.drawEllipse(0,0,20,20)
        qp.end()
        self.status_dot.setPixmap(pm)

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            # here you would call real check
            ok = bool(int(time.time()) % 2)  # fake alternating status
            self._set_status(ok)
            self.remaining = CHECK_INTERVAL
        self.timer_pill.set_remaining(self.remaining)

    # allow dragging
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and hasattr(self, "_drag_offset"):
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        if hasattr(self, "_drag_offset"):
            delattr(self, "_drag_offset")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = StatusWidget()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
