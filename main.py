from __future__ import annotations
import os, sys, time, threading
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from path import *
from cycle import *

# ====== Config ======
ICON_SIZE = 64
DETAIL_WIDTH = 400
EXPANDED_MIN_HEIGHT = 150

# 24시간(초)
CHECK_INTERVAL_SEC = 24 * 60 * 60  # 86400

# 폴더 열기 기본 경로
FOLDER_TO_OPEN = BASE_RECORD

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
    def _update(self): self.setText("+" if not self._expanded else "−"); self.setToolTip("확장" if not self._expanded else "축소")

class DetailPanel(QtWidgets.QFrame):
    def __init__(self, width: int = DETAIL_WIDTH):
        super().__init__(); self._maxw = width
        self.setMinimumWidth(1); self.setMaximumWidth(1)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.setStyleSheet(
            "background:rgba(28,30,36,235);"
            "border-top-right-radius:12px; border-bottom-right-radius:12px;"
            "border-left:1px solid rgba(255,255,255,26);"
        )
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(28, 14, 16, 14)
        lay.setSpacing(8)

        # 상태 라벨 (자동 개행 X → 잘리도록 설정)
        self.lbl_status = QtWidgets.QLabel("— 스레드 동작 상태 —   스케줄러: 실행 중 (대기 --:--)")
        self.lbl_status.setStyleSheet(
            "color:#cfd2d8; font-size:12px; font-family: Consolas, monospace;"
        )
        self.lbl_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_status.setWordWrap(False)   # ✅ 자동 줄바꿈 해제
        self.lbl_status.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        self.lbl_status.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 선택 가능(옵션)

        lay.addWidget(self.lbl_status)
        lay.addStretch(1)




# -------------------- Main HUD --------------------
class HUD(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._first_show = True

        # state
        self._ok = True
        self._next_ts = time.time() + CHECK_INTERVAL_SEC   # 시작 시 무조건 지금 + 24h
        #self._next_ts = time.time() + 5   # developer mode
        self._ts_lock = threading.RLock()

        self._last_cycle_at: float | None = None
        self._last_cycle_ok: bool | None = None
        self._active_workers: int = 0
        self._last_run_msg: str = ""

        # left side widgets
        self.icon = IconCircle()
        self.dot = StatusDot()
        self.title = QtWidgets.QLabel("Pi manager"); self.title.setStyleSheet("color:#dfe2e8; font-weight:700; font-size:12px; letter-spacing:0.6px;")
        self.label_next = QtWidgets.QLabel(); self.label_next.setStyleSheet("color:#dfe2e8; font-size:12px;")
        self._update_next_label()

        # buttons (제목 오른쪽): 체크, 폴더, 플러스
        self.btn_check = RoundIconButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), "지금 바로 체크")
        self.btn_folder = RoundIconButton(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon), "기록 폴더 열기")
        self.btn_plus = PlusButton()

        # 전원 버튼(맨 왼쪽, 은은한 빨강)
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
        self.btn_check.clicked.connect(self._manual_check)
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
        pw_lay.setContentsMargins(0, 4, 0, 0)
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
        self._expanded_size = QtCore.QSize(
            self._collapsed_size.width() + self.detail._maxw,
            max(self._collapsed_size.height(), EXPANDED_MIN_HEIGHT)
        )

        global EXPANDED_WINDOW_SIZE, COLLAPSED_WINDOW_SIZE
        EXPANDED_WINDOW_SIZE, COLLAPSED_WINDOW_SIZE = self._expanded_size, self._collapsed_size

        # UI 라벨 갱신 타이머(표시만)
        self._tick = QtCore.QTimer(self)
        self._tick.timeout.connect(self._update_next_label)
        self._tick.start(1000)

        self._status_tick = QtCore.QTimer(self)
        self._status_tick.timeout.connect(self._update_status_label)
        self._status_tick.start(1000)
        self._update_status_label()  # 초기 1회

        # 백그라운드 스케줄러 스레드 시작
        self._stop_evt = threading.Event()
        self._sched_th = threading.Thread(target=self._scheduler_loop, name="daily-scheduler", daemon=True)
        self._sched_th.start()

        # ===== 드래그 상태 & 이벤트 필터 등록 =====
        self._dragging = False
        self._drag_offset = QtCore.QPoint()

        # 전체 영역에서 끌 수 있도록 큰 컨테이너들에 필터 설치
        self.installEventFilter(self)
        self.card.installEventFilter(self)
        self.left.installEventFilter(self)
        self.detail.installEventFilter(self)

    def eventFilter(self, obj, event):
        # 좌클릭 눌렀을 때: 드래그 시작
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._dragging = True
            # 현재 커서의 전역 좌표 - 창의 좌상단 오프셋 저장
            # (PySide6: globalPosition() -> QPointF)
            gp = event.globalPosition().toPoint()
            self._drag_offset = gp - self.frameGeometry().topLeft()
            return True  # 이벤트 소진(기본 처리 막음)

        # 마우스 이동 중: 드래그이면 창 이동
        if event.type() == QtCore.QEvent.MouseMove and self._dragging:
            gp = event.globalPosition().toPoint()
            self.move(gp - self._drag_offset)
            return True

        # 버튼 떼면: 드래그 종료
        if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self._dragging = False
            return True

        return super().eventFilter(obj, event)

    # ---------------- Scheduler -----------------
    def _scheduler_loop(self):
        while not self._stop_evt.is_set():
            with self._ts_lock:
                target = self._next_ts
            now = time.time()
            if now >= target:
                # 예약 시간 도달 → 사이클 수행 후 +24h 재설정
                self._run_cycle()
                with self._ts_lock:
                    self._next_ts = time.time() + CHECK_INTERVAL_SEC
                continue
            # 남은 시간만큼 짧게 대기(최대 5초 단위로 깨어나 확인)
            wait_s = min(max(target - now, 0.0), 5.0)
            self._stop_evt.wait(wait_s)

    def _run_cycle(self):
        self._move_to_top_left()
        isRunning = None
        ok = False
        try:
            isRunning = check()
            ok = True
        except Exception as e:
            print(f"[scheduler] cycle error: {e}")
        finally:
            self._last_cycle_ok = ok
            self._last_cycle_at = time.time()

            if isRunning is True:
                self._last_run_msg = "프로그램이 정상 동작 중입니다."
            elif isRunning is False:
                self._last_run_msg = "프로그램이 정상 동작 중이지 않습니다."

            QtCore.QMetaObject.invokeMethod(
                self, "_update_status_label", Qt.QueuedConnection
            )

    # ---------------- UI Events -----------------
    def _manual_check(self):
        threading.Thread(target=self._manual_worker, daemon=True).start()

    def _manual_worker(self):
        self._active_workers += 1
        self._update_status_label()
        try:
            self._run_cycle()
            with self._ts_lock:
                self._next_ts = time.time() + CHECK_INTERVAL_SEC
        finally:
            self._active_workers -= 1
            self._update_status_label()


    def _move_to_top_left(self):
        screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.left(), screen.top())

    def showEvent(self, e):
        super().showEvent(e)
        if self._first_show:
            self._first_show = False
            self.detail.setVisible(False)
            self.detail.setMinimumWidth(1); self.detail.setMaximumWidth(1)
            self.resize(self._collapsed_size)
            self.card.updateGeometry()
            if self.layout(): self.layout().activate()
            self._move_to_top_left()

    # helpers
    def _format_next(self, ts: float) -> str:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("다음 체크 시간 %m월 %d일 %H시 %M분")

    def _fmt_hms(self, secs: float) -> str:
        secs = max(0, int(secs))
        h, r = divmod(secs, 3600)
        m, s = divmod(r, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _status_line(self) -> str:
        # 스케줄러
        alive = self._sched_th.is_alive() if hasattr(self, "_sched_th") else False
        with self._ts_lock:
            remain = max(0.0, self._next_ts - time.time())

        sched = f"스케줄러: {'실행 중' if alive else '중지됨'} (대기 {self._fmt_hms(remain)})"

        # 최근 사이클
        if self._last_cycle_at is None:
            last = "최근 사이클: 기록 없음"
        else:
            dt = datetime.fromtimestamp(self._last_cycle_at)
            when = dt.strftime("%m월 %d일 %H:%M:%S")
            result = "성공" if self._last_cycle_ok else "실패"
            last = f"최근 사이클: {when} · {result}"

        # 수동 작업
        workers = f"백그라운드 작업(수동): {self._active_workers}개"

        # UI 타이머
        ui_tick = "활성" if self._tick.isActive() else "비활성"
        ui_line = f"UI 타이머: {ui_tick}"

        # 다음 체크 절대시각(상단에도 보이지만 상세에 한번 더)
        with self._ts_lock:
            nxt = self._format_next(self._next_ts)

        lines = [
            "— 스레드 동작 상태 —",
            sched,
            workers,
            ui_line,
            last,
            nxt,
        ]
        return "\n".join(lines)

    def _update_status_label(self):
        with self._ts_lock:
            remain = max(0, int(self._next_ts - time.time()))
        h, r = divmod(remain, 3600)
        m, s = divmod(r, 60)
        remain_str = f"{h:02d}:{m:02d}:{s:02d}"

        # 기존 두 줄 + 결과 문구
        text = (
            "— 스레드 동작 상태 —   \n"
            f"스케줄러: 실행 중 (대기 {remain_str})"
        )
        if self._last_run_msg:
            text += f"\n{self._last_run_msg}"

        self.detail.lbl_status.setText(text)




    def _update_next_label(self):
        with self._ts_lock:
            ts = self._next_ts
        self.label_next.setText(self._format_next(ts))

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

    def closeEvent(self, e: QtGui.QCloseEvent):
        # 앱 종료 시 스케줄러 안전 종료
        if hasattr(self, "_stop_evt"):
            self._stop_evt.set()
        return super().closeEvent(e)


def start():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = HUD(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print_all_paths()
    check_exe_path()
    start()
