from __future__ import annotations
import os, sys, time
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from path import *  # ICON, OPEN_DIR 등 있으면 사용

# ====== Config ======
ICON_SIZE = 64
CHECK_INTERVAL_SEC = 60

DETAIL_WIDTH = 1000          # 확장 시 오른쪽 패널 목표 폭
EXPANDED_MIN_HEIGHT = 260    # 확장 최소 높이

# 폴더 열기 기본 경로
FOLDER_TO_OPEN = (
    globals().get("OPEN_DIR")
    or globals().get("FOLDER_PATH")
    or globals().get("TARGET_DIR")
    or globals().get("OPEN_PATH")
    or os.path.expanduser("~")
)

# (optional) 전역 사이즈
EXPANDED_WINDOW_SIZE: QtCore.QSize | None = None
COLLAPSED_WINDOW_SIZE: QtCore.QSize | None = None


# -------------------- UI Building Blocks --------------------
class GlassCard(QtWidgets.QWidget):
    """좌측/우측(detail)을 담는 카드. 간격은 0(접힘/펼침 공통)로 고정."""
    def __init__(self, *widgets: QtWidgets.QWidget):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(0)  # 덜컹 방지: 레이아웃 간격을 고정 0
        for w in widgets:
            lay.addWidget(w, 0, Qt.AlignTop)  # 상단 고정
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        r = self.rect().adjusted(2, 2, -2, -2)
        grad = QtGui.QLinearGradient(r.topLeft(), r.bottomLeft())
        grad.setColorAt(0.0, QtGui.QColor(30,32,38,235))
        grad.setColorAt(1.0, QtGui.QColor(24,26,32,235))
        p.setPen(Qt.NoPen); p.setBrush(grad)
        p.drawRoundedRect(r, 14, 14)
        p.setPen(QtGui.QPen(QtGui.QColor(255,255,255,26), 1))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRoundedRect(r, 14, 14)

class IconCircle(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        pad = 10
        self.setFixedSize(ICON_SIZE + pad*2, ICON_SIZE + pad*2)
        self._pix = QtGui.QPixmap(ICON) if os.path.exists(ICON) else None

    def paintEvent(self, e):
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect().adjusted(2,2,-2,-2)
        p.setPen(Qt.NoPen); p.setBrush(QtGui.QColor(22,24,29,220))
        p.drawEllipse(rect)
        inner = rect.adjusted(10,10,-10,-10)
        if self._pix and not self._pix.isNull():
            pix = self._pix.scaled(inner.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.drawPixmap(inner.center().x()-pix.width()//2, inner.center().y()-pix.height()//2, pix)
        else:
            path = QtGui.QPainterPath(); r = inner
            path.moveTo(r.center().x()-r.width()*0.15, r.top()+r.height()*0.2)
            path.lineTo(r.center().x()+r.width()*0.05, r.center().y()-r.height()*0.05)
            path.lineTo(r.center().x()-r.width()*0.02, r.center().y())
            path.lineTo(r.center().x()+r.width()*0.15, r.bottom()-r.height()*0.2)
            path.lineTo(r.center().x()-r.width()*0.05, r.center().y()+r.height()*0.05)
            path.closeSubpath(); p.setBrush(QtGui.QColor(235,235,240)); p.drawPath(path)

class StatusDot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.setFixedSize(22,22); self._ok = True
    def set_ok(self, ok: bool): self._ok = bool(ok); self.update()
    def paintEvent(self, e):
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect().adjusted(2,2,-2,-2)
        color = QtGui.QColor(72,201,115) if self._ok else QtGui.QColor(231,76,60)
        p.setPen(Qt.NoPen); p.setBrush(color); p.drawEllipse(rect)

class RoundIconButton(QtWidgets.QToolButton):
    """아이콘 전용 원형 버튼(28px)."""
    def __init__(self, icon: QtGui.QIcon | None = None, tooltip: str = "", style_override: str = ""):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(28, 28)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(16, 16))
        if icon:
            self.setIcon(icon)
        if tooltip:
            self.setToolTip(tooltip)
        base_style = """
            QToolButton { background:#2c2e37; color:#e8e8ea;
                          border:1px solid #3a3d48; border-radius:14px; }
            QToolButton:hover { background:#3a3d48; }
            QToolButton:pressed { background:#24262e; }
        """
        self.setStyleSheet(style_override or base_style)

class PlusButton(QtWidgets.QToolButton):
    def __init__(self):
        super().__init__(); self._expanded = False
        self.setCursor(Qt.PointingHandCursor); self.setFixedSize(28,28)
        self.setStyleSheet("""
            QToolButton { background:#2c2e37; color:#e8e8ea; border:1px solid #3a3d48; border-radius:14px; font-weight:700; }
            QToolButton:hover { background:#3a3d48; } QToolButton:pressed { background:#24262e; }
        """); self._update()
    def set_expanded(self, v: bool): self._expanded = bool(v); self._update()
    def _update(self): self.setText("+" if not self._expanded else "−"); self.setToolTip("열기" if not self._expanded else "닫기")

class DetailPanel(QtWidgets.QFrame):
    def __init__(self, width: int = DETAIL_WIDTH):
        super().__init__(); self._maxw = width
        self.setMinimumWidth(1); self.setMaximumWidth(1)  # 시작은 접힘
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        # 경계 이음새 + 내부 패딩
        self.setStyleSheet(
            "background:rgba(28,30,36,235);"
            "border-top-right-radius:12px; border-bottom-right-radius:12px;"
            "border-left:1px solid rgba(255,255,255,26);"
        )
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(28, 14, 16, 14)  # 왼쪽 패딩 약간 크게
        lay.setSpacing(8)
        title = QtWidgets.QLabel("상세 디테일")
        title.setStyleSheet("color:#f0f0f3; font-weight:700; font-size:13px;")
        desc = QtWidgets.QLabel("여기에 상세 정보를 구성하세요. 로그, 버튼, 링크 등…")
        desc.setStyleSheet("color:#cfd2d8; font-size:12px;")
        desc.setWordWrap(False); desc.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        lay.addWidget(title); lay.addWidget(desc); lay.addStretch(1)


# -------------------- Main HUD --------------------
class HUD(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._first_show = True  # 반드시 접힌 상태로 보이게

        # state
        self._ok = True
        self._interval = CHECK_INTERVAL_SEC
        self._next_ts = time.time() + self._interval

        # left side widgets
        self.icon = IconCircle()
        self.dot = StatusDot()
        self.title = QtWidgets.QLabel("Pi manager"); self.title.setStyleSheet("color:#dfe2e8; font-weight:700; font-size:12px; letter-spacing:0.6px;")
        self.label_next = QtWidgets.QLabel(); self.label_next.setStyleSheet("color:#dfe2e8; font-size:12px;")
        self._update_next_label()

        # buttons (제목 오른쪽): 체크, 폴더, 플러스
        self.btn_check = RoundIconButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), "체크 (로그)")
        self.btn_folder = RoundIconButton(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon), "폴더 열기")
        self.btn_plus = PlusButton()

        # ★ 전원 버튼(맨 왼쪽, 은은한 빨강)
        power_style = """
            QToolButton { background:#3a1f1f; color:#f5eaea;
                          border:1px solid #6e2c2c; border-radius:14px; }
            QToolButton:hover { background:#4b2323; }
            QToolButton:pressed { background:#2f1818; }
        """
        self.btn_power = RoundIconButton(None, "종료", style_override=power_style)
        self.btn_power.setText("⏻")  # 전원 심볼
        self.btn_power.setStyleSheet(power_style + "QToolButton { font-weight:700; }")

        # wiring
        self.btn_plus.clicked.connect(self._toggle_detail)
        self.btn_folder.clicked.connect(self._open_folder)
        self.btn_check.clicked.connect(lambda: self._log("✔ 체크 버튼 클릭"))
        self.btn_power.clicked.connect(QtWidgets.QApplication.quit)

        # title/status rows
        title_row = QtWidgets.QHBoxLayout(); title_row.setContentsMargins(0,0,0,0); title_row.setSpacing(8)
        title_row.addWidget(self.title); title_row.addStretch(1)
        title_row.addWidget(self.btn_check)
        title_row.addWidget(self.btn_folder)
        title_row.addWidget(self.btn_plus)

        status_row = QtWidgets.QHBoxLayout(); status_row.setContentsMargins(0,0,0,0); status_row.setSpacing(8)
        status_row.addWidget(self.dot); status_row.addWidget(self.label_next); status_row.addStretch(1)

        right = QtWidgets.QWidget(); right_col = QtWidgets.QVBoxLayout(right)
        right_col.setContentsMargins(0,0,0,0); right_col.setSpacing(6)
        right_col.addLayout(title_row); right_col.addLayout(status_row)

        # 좌측 컨테이너(전원 버튼 + 아이콘 + 텍스트) — 폭 고정
        self.left = QtWidgets.QWidget()
        left_row = QtWidgets.QHBoxLayout(self.left)
        left_row.setContentsMargins(0,0,0,0); left_row.setSpacing(10)
        left_row.addWidget(self.btn_power)  # 맨 왼쪽
        
        power_wrap = QtWidgets.QWidget()
        pw_lay = QtWidgets.QVBoxLayout(power_wrap)
        pw_lay.setContentsMargins(0, 4, 0, 0)   # ↑ 여기 숫자(4)를 키우면 더 내려가고, 줄이면 더 올라감 (2~10 추천)
        pw_lay.setSpacing(0)
        pw_lay.addWidget(self.btn_power, 0, Qt.AlignLeft | Qt.AlignTop)
        pw_lay.addStretch(1)
        left_row.addWidget(power_wrap)
        left_row.addWidget(self.icon)
        left_row.addWidget(right)
        self.left.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)

        # detail (collapsed)
        self.detail = DetailPanel(DETAIL_WIDTH)  # min/max=1로 시작(접힘)

        # card
        self.card = GlassCard(self.left, self.detail)
        root = QtWidgets.QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.addWidget(self.card)

        # 좌측 고정폭 확정 → 원래 레이아웃 유지
        self.adjustSize()
        self.left.setFixedWidth(self.left.sizeHint().width())
        self.adjustSize()

        # --- 접힘/펼침 사이즈 계산 ---
        self._collapsed_size = self.size()

        # 🔒 초기에는 detail을 전혀 건드리지 않고 '펼침 크기'를 산술로 계산 → 시작부터 넓어지는 문제 방지
        self._expanded_size = QtCore.QSize(
            self._collapsed_size.width() + self.detail._maxw,
            max(self._collapsed_size.height(), EXPANDED_MIN_HEIGHT)
        )

        # 전역 저장
        global EXPANDED_WINDOW_SIZE, COLLAPSED_WINDOW_SIZE
        EXPANDED_WINDOW_SIZE, COLLAPSED_WINDOW_SIZE = self._expanded_size, self._collapsed_size

        # 메뉴/타이머
        self.menu = QtWidgets.QMenu(); self.menu.addAction("Check now", self._on_check_now); self.menu.addAction("Quit", QtWidgets.QApplication.quit)
        self._tick = QtCore.QTimer(self); self._tick.timeout.connect(self._on_tick); self._tick.start(1000)

    def showEvent(self, e):
        super().showEvent(e)
        if self._first_show:
            self._first_show = False
            # 접힌 상태로 보이기 + 중앙 배치 (완전히 스냅)
            self.detail.setVisible(False)
            self.detail.setMinimumWidth(1); self.detail.setMaximumWidth(1)
            self.resize(self._collapsed_size)
            self.card.updateGeometry()
            if self.layout(): self.layout().activate()
            self._move_to_screen_center(self._collapsed_size)

    def _move_to_screen_center(self, size: QtCore.QSize):
        screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - size.width() // 2,
                  screen.center().y() - size.height() // 2)

    # helpers
    def _format_next(self, ts: float) -> str:
        return datetime.fromtimestamp(ts).strftime("다음 체크 시간 %m월 %d일 %H시 %M분")
    def _update_next_label(self): self.label_next.setText(self._format_next(self._next_ts))
    def _log(self, msg: str): print(f"[PiManagerHUD] {msg}")

    # open folder (파일 탐색기)
    def _open_folder(self):
        path = str(FOLDER_TO_OPEN)
        if not path or not os.path.exists(path):
            self._log(f"폴더 경로 없음: {path}")
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "경로가 없습니다.")
            return
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))
        self._log(f"폴더 열기: {path}")

    # expand/collapse
    def _toggle_detail(self):
        expanding = not self.detail.isVisible()
        if expanding:
            self.detail.setVisible(True)

        # detail 폭 애니 (min/max 동시)
        anim_min = QtCore.QPropertyAnimation(self.detail, b"minimumWidth", self)
        anim_min.setDuration(260)
        anim_min.setStartValue(max(1, self.detail.minimumWidth()))
        anim_min.setEndValue(self.detail._maxw if expanding else 1)
        anim_min.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        anim_max = QtCore.QPropertyAnimation(self.detail, b"maximumWidth", self)
        anim_max.setDuration(260)
        anim_max.setStartValue(max(1, self.detail.maximumWidth()))
        anim_max.setEndValue(self.detail._maxw if expanding else 1)
        anim_max.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        # 창 크기 애니(좌상단 고정, 우/하로만 변화)
        top_left = self.frameGeometry().topLeft()
        start = QtCore.QRect(top_left, self.size())
        end_size = self._expanded_size if expanding else self._collapsed_size
        end = QtCore.QRect(top_left, end_size)
        anim_geom = QtCore.QPropertyAnimation(self, b"geometry", self)
        anim_geom.setDuration(260); anim_geom.setStartValue(start); anim_geom.setEndValue(end)
        anim_geom.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        grp = QtCore.QParallelAnimationGroup(self)
        grp.addAnimation(anim_min); grp.addAnimation(anim_max); grp.addAnimation(anim_geom)

        def _finish():
            if not expanding:
                self.detail.setVisible(False)
            self.setGeometry(end)  # 스냅
            self.card.updateGeometry()
            if self.layout(): self.layout().activate()

        grp.finished.connect(_finish)
        self.btn_plus.set_expanded(expanding)
        self._anim = grp; grp.start()

    # logic demo
    def perform_check(self) -> bool:
        self._ok = not self._ok; return self._ok
    def _on_tick(self):
        if time.time() >= self._next_ts:
            self.dot.set_ok(self.perform_check()); self._next_ts = time.time() + self._interval; self._update_next_label()
    def _on_check_now(self):
        self.dot.set_ok(self.perform_check()); self._next_ts = time.time() + self._interval; self._update_next_label()

    # drag/menu
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
        elif e.button() == Qt.RightButton:
            self.menu.popup(e.globalPosition().toPoint())
    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and hasattr(self, "_drag"):
            self.move(e.globalPosition().toPoint() - self._drag)
    def mouseReleaseEvent(self, e):
        if hasattr(self, "_drag"): delattr(self, "_drag")


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = HUD(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
