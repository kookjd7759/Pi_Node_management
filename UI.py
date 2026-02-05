import sys
import os
from datetime import datetime
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, 
    QApplication, QWidget, QMainWindow,
    QPushButton, QLabel, QStackedWidget, QComboBox,
    QFrame, QSizePolicy, QLineEdit, QTextEdit
)

import program
import config
import path

class MainWindow(QMainWindow):
    def closeEvent(self, event):
        program.terminate()
        event.accept()

    def _raise(self):
        self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()

    def init_item(self):
        for value in range(0, 24):
            key = f'{value:02}:00'
            self.item_check_time_key.append(key)
            self.item_check_time_value.append(value)

    def __init__(self):
        super().__init__()
        config.init()
        program.init()
        self._raise()

        self.setWindowTitle('Pi Node Manager')
        self.setWindowIcon(QIcon(path.ICON))
        self.resize(900, 520)

        # ---- item init
        self.item_check_time_key = []
        self.item_check_time_value = []
        self.init_item()

        # ---- global style
        self.setStyleSheet("""
        /* ====== Global ====== */
        QMainWindow, QWidget {
            background: #0B1220;
            color: #EAF0FF;
            font-family: "Segoe UI", "Pretendard", "Noto Sans KR";
            font-size: 14px;
            border-radius: 18px;
        }
        QLabel { background: transparent; }
        /* ====== Left Sidebar ====== */
        QFrame#Sidebar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0F1A2F, stop:1 #0B1220);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }
W
        QLabel#BrandTitle {
            font-size: 18px;W
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        QLabel#BrandSub {
            color: rgba(234,240,255,0.70);
            font-size: 11px;
        }
        QFrame#BrandLine {
            background: rgba(255,255,255,0.08);
            border-radius: 2px;
        }

        QPushButton#NavButton {
            text-align: left;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.06);
            background: rgba(255,255,255,0.03);
            color: rgba(234,240,255,0.92);
            font-weight: 700;
        }
        QPushButton#NavButton:hover {
            background: rgba(120,180,255,0.10);
            border: 1px solid rgba(120,180,255,0.30);
        }
        QPushButton#NavButton:pressed {
            background: rgba(120,180,255,0.18);
            border: 1px solid rgba(120,180,255,0.35);
        }
        /* ✅ Selected (checked) Nav Button */
        QPushButton#NavButton:checked {
            background: rgba(120,180,255,0.22);
            border: 1px solid rgba(120,180,255,0.55);
            color: rgba(234,240,255,1.0);
        }

        /* ====== Content Area ====== */
        QFrame#ContentShell {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        QLabel#PageTitle {
            font-size: 16px;
            font-weight: 800;
        }
        QLabel#PageHint {
            color: rgba(234,240,255,0.72);
            font-size: 11px;
        }

        QFrame#Card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        /* ====== Action Buttons ====== */
        QPushButton#ActionPrimary {
            padding: 14px 16px;
            border-radius: 18px;
            border: 2px solid rgba(80,160,255,1);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2E6AE6,
                        stop:1 #00BFE0);
            font-weight: 900;
            letter-spacing: 0.2px;
        }
        QPushButton#ActionPrimary:hover {
            border: 2px solid rgba(120,200,255,1);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(66,133,244,0.70),
                        stop:1 rgba(0,220,255,0.45));
        }
        QPushButton#ActionPrimary:pressed {
            background: rgba(66,133,244,0.35);
        }

        QPushButton#ActionSecondary {
            padding: 14px 16px;
            border-radius: 18px;
            border: 1px solid rgba(80,80,80,1);
            background: rgba(255,255,255,0.04);;
            font-weight: 800;
        }
        QPushButton#ActionSecondary:hover {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(80,80,80,1);
        }
        QPushButton#ActionSecondary:pressed {
            background: rgba(255,255,255,0.03);
        }

        /* ====== ComboBox ====== */
        QComboBox {
            padding: 10px 12px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.03);
            font-weight: 700;
        }
        QComboBox:hover {
            border: 1px solid rgba(120,180,255,0.30);
        }
        QComboBox QAbstractItemView {
            background: #0E1830;
            border: 1px solid rgba(255,255,255,0.10);
            selection-background-color: rgba(120,180,255,0.20);
            selection-color: #EAF0FF;
            outline: none;
        }

        /* ====== Small text labels ====== */
        QLabel#FieldLabel {
            color: rgba(234,240,255,0.80);
            font-weight: 800;
        }
        
        QWidget#TopRow {
            background: transparent;
            border-radius: 18px;
        }
                           
        /* ====== Dashboard Image Card ====== */
        QFrame#ImageCard {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }
        QLabel#ImageView {
            border-radius: 16px; /* 카드 안쪽 이미지 둥글게 */
        }
        """)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        # ---- left menu (Sidebar)
        left = QFrame()
        left.setObjectName("Sidebar")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        left.setFixedWidth(220)

        # Brand block
        brand = QWidget()
        brand.setStyleSheet("background: transparent;")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(6, 6, 6, 6)
        brand_layout.setSpacing(6)

        title = QLabel("Pi Node Manager")
        title.setObjectName("BrandTitle")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        sub = QLabel("Pi( π ) Coin Mining Manager")
        sub.setObjectName("BrandSub")
        sub.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        line = QFrame()
        line.setObjectName("BrandLine")
        line.setFixedHeight(3)

        brand_layout.addWidget(title)
        brand_layout.addWidget(sub)
        brand_layout.addWidget(line)

        btn_dashboard = QPushButton("  ⚡  Dashboard")
        btn_setting = QPushButton("  ⚙️  Setting")
        btn_dashboard.setObjectName("NavButton")
        btn_setting.setObjectName("NavButton")

        # ✅ Highlight only selected page (no UI/function change except selection state)
        btn_dashboard.setCheckable(True)
        btn_setting.setCheckable(True)
        btn_dashboard.setAutoExclusive(True)
        btn_setting.setAutoExclusive(True)
        btn_dashboard.setChecked(True)

        btn_dev = QPushButton("  💻🛠️  Developer")
        btn_dev.setObjectName("NavButton")

        btn_dev.setCheckable(True)
        btn_dev.setAutoExclusive(True)

        left_layout.addWidget(brand)
        left_layout.addSpacing(6)
        left_layout.addWidget(btn_dashboard)
        left_layout.addWidget(btn_setting)
        left_layout.addWidget(btn_dev)
        left_layout.addStretch()

        footer = QLabel("v0.5.4 target • Pi Node Manager")
        footer.setStyleSheet("color: rgba(234,240,255,0.45); font-size: 10px;")
        left_layout.addWidget(footer)

        # ---- right content shell
        content_shell = QFrame()
        content_shell.setObjectName("ContentShell")
        content_layout = QVBoxLayout(content_shell)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(14)

                # Header inside content
        header = QWidget()
        header.setStyleSheet("background: transparent;")

        # ✅ header top row: title + clock (right)
        header_top = QWidget()
        header_top.setStyleSheet("background: transparent;")
        header_top_layout = QHBoxLayout(header_top)
        header_top_layout.setContentsMargins(6, 2, 6, 2)
        header_top_layout.setSpacing(8)

        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("PageTitle")

        # ✅ realtime clock label
        self.header_clock = QLabel("")
        self.header_clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_clock.setStyleSheet("""
            color: rgba(234,240,255,0.75);
            font-weight: 800;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
        """)

        header_top_layout.addWidget(self.header_title)
        header_top_layout.addStretch(1)
        header_top_layout.addWidget(self.header_clock)

        # ✅ header bottom row: hint
        header_bottom = QWidget()
        header_bottom.setStyleSheet("background: transparent;")
        header_bottom_layout = QVBoxLayout(header_bottom)
        header_bottom_layout.setContentsMargins(6, 0, 6, 2)
        header_bottom_layout.setSpacing(2)

        self.header_hint = QLabel("Quick actions for Managing")
        self.header_hint.setObjectName("PageHint")
        header_bottom_layout.addWidget(self.header_hint)

        # ✅ pack header
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        header_layout.addWidget(header_top)
        header_layout.addWidget(header_bottom)

        # ---- pages
        self.pages = QStackedWidget()
        self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pages.addWidget(self.page_main())
        self.pages.addWidget(self.page_settings())
        self.pages.addWidget(self.page_dev())

        content_layout.addWidget(header)
        content_layout.addWidget(self.pages, 1)

        # ---- signals (keep existing behavior)
        btn_dashboard.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        btn_setting.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        btn_dev.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        btn_dev.clicked.connect(lambda: btn_dev.setChecked(True))
        btn_dev.clicked.connect(lambda: self._set_header("Developer", "Diagnostics / paths / runtime status."))


        # ✅ ensure checked highlight follows navigation
        btn_dashboard.clicked.connect(lambda: btn_dashboard.setChecked(True))
        btn_setting.clicked.connect(lambda: btn_setting.setChecked(True))

        # (UI only) Update header text on navigation (does not change any existing functions)
        btn_dashboard.clicked.connect(lambda: self._set_header("Dashboard", "Quick actions for capture / open / restart."))
        btn_setting.clicked.connect(lambda: self._set_header("Setting", "Set the daily checking time."))

        # ---------- layout ----------
        root_layout.addWidget(left)
        root_layout.addWidget(content_shell, 1)

        # ✅ realtime clock (update every 500ms)
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(500)
        self._update_clock()
        
        # ✅ schedule capture (check every 30s)
        self._last_auto_capture_date = None
        self._sched_timer = QTimer(self)
        self._sched_timer.timeout.connect(self._schedule_tick)
        self._sched_timer.start(30_000) 
        self._schedule_tick()

        self.setCentralWidget(root)

    def _set_header(self, t, h):
        self.header_title.setText(t)
        self.header_hint.setText(h)

    def page_main(self):
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(14)

        # Card container
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(14)

        top_row = QWidget()
        top_row.setObjectName("TopRow")
        top_row.setAttribute(Qt.WA_StyledBackground, True)
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(12)

        btn_capture = QPushButton('📸 CAPTURE\nMining state')
        btn_capture.setObjectName("ActionPrimary")
        btn_capture.setMinimumHeight(92)
        btn_capture.clicked.connect(self.function_btn_capture)

        btn_maxi_node = QPushButton('⬜ MAXIMIZE\nPi node window')
        btn_maxi_node.setObjectName("ActionSecondary")
        btn_maxi_node.setMinimumHeight(92)
        btn_maxi_node.clicked.connect(self.function_btn_maxi_node)

        btn_mini_node = QPushButton('➖ MINIMIZE\nPi node window')
        btn_mini_node.setObjectName("ActionSecondary")
        btn_mini_node.setMinimumHeight(92)
        btn_mini_node.clicked.connect(self.function_btn_mini_node)

        btn_restart_node = QPushButton('🔁 RESTART\nPi node')
        btn_restart_node.setObjectName("ActionSecondary")
        btn_restart_node.setMinimumHeight(92)
        btn_restart_node.clicked.connect(self.function_btn_restart_node)

        btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_maxi_node.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_restart_node.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        top_row_layout.addWidget(btn_capture, 2)
        top_row_layout.addWidget(btn_maxi_node, 1)
        top_row_layout.addWidget(btn_mini_node, 1)
        top_row_layout.addWidget(btn_restart_node, 1)

        info = QFrame()
        info.setStyleSheet("background: transparent; border: none;")
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(10)

        hint = QLabel("● Capture first, then restart if the node looks stuck.")
        hint.setStyleSheet("color: rgba(234,240,255,0.75); font-weight: 700;")
        info_layout.addWidget(hint)
        info_layout.addStretch()

        card_layout.addWidget(top_row)
        card_layout.addWidget(info)

        outer.addWidget(card)

        status_row = QFrame()
        status_row.setObjectName("Card")
        status_layout = QHBoxLayout(status_row)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(10)

        status_label = QLabel("Current Node status")
        status_label.setObjectName("FieldLabel")

        # [⚪ Not checked yet], [🟢 Mining Online], [🔴 Mining Offline], [🟡 Checking...]
        self.line_status = QLineEdit("⚪ Not checked yet")
        self.line_status.setReadOnly(True)
        self.line_status.setFocusPolicy(Qt.NoFocus)
        self.line_status.setCursorPosition(0)
        self.line_status.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.10);
                background: rgba(255,255,255,0.03);
                color: rgba(234,240,255,0.92);
                font-weight: 800;
            }
        """)

        status_layout.addWidget(status_label)
        btn_check_status = QPushButton("🔎 Check")
        btn_check_status.setObjectName("ActionSecondary")
        btn_check_status.setMinimumHeight(40)
        btn_check_status.clicked.connect(self.function_btn_check_status)

        status_layout.addSpacing(10)
        status_layout.addWidget(btn_check_status)

        status_layout.addStretch(1)
        status_layout.addWidget(self.line_status, 0)


        outer.addWidget(status_row)

        img_card = QFrame()
        img_card.setObjectName("ImageCard")
        img_card_layout = QVBoxLayout(img_card)
        img_card_layout.setContentsMargins(12, 12, 12, 12)
        img_card_layout.setSpacing(8)
        
        self.img_title = QLabel("Recent status capture image")
        self.img_title.setStyleSheet("color: rgba(234,240,255,0.80); font-weight: 800;")
        img_card_layout.addWidget(self.img_title)
        
        self.dashboard_img = QLabel()
        self.dashboard_img.setObjectName("ImageView")
        self.dashboard_img.setAlignment(Qt.AlignCenter)
        self.dashboard_img.setScaledContents(True)
        self.dashboard_img.setMinimumHeight(220)
        self.dashboard_img.setStyleSheet("""
            QLabel#ImageView {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.06);
            }
        """)
        screen = QApplication.primaryScreen()
        size = screen.size()
        bw = max(200, size.width() // 3)
        bh = max(200, size.height() // 3)

        self.dashboard_img.setFixedSize(bw, bh)
        
        img_card_layout.addWidget(self.dashboard_img)
        outer.addWidget(img_card)

        self._update_recent_capture()

        outer.addStretch()
        return w
    
    def page_settings(self):
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(14)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        # Title inside card (UI only)
        title = QLabel("Checking time")
        title.setStyleSheet("background: transparent;")
        title.setObjectName("FieldLabel")

        subtitle = QLabel("Select the hour to run your routine check.")
        subtitle.setStyleSheet("background: transparent; color: rgba(234,240,255,0.65); font-size: 11px;")

        self.combo_time = QComboBox()
        self.combo_time.addItems(self.item_check_time_key)
        self.combo_time.setCurrentIndex(config.get_check_time())
        self.combo_time.currentIndexChanged.connect(self.function_comboBox_select_item)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.combo_time)

        # bottom hint bar
        tip = QFrame()
        tip.setStyleSheet("background: transparent; border: none;")
        tip_layout = QHBoxLayout(tip)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(8)

        msg = QLabel("● Saved instantly when you change the value.")
        msg.setStyleSheet("color: rgba(234,240,255,0.75); font-weight: 700;")
        tip_layout.addWidget(msg)
        tip_layout.addStretch()

        card_layout.addSpacing(10)
        card_layout.addWidget(tip)

        outer.addWidget(card)
        outer.addStretch()

        return w
    
    def page_dev(self):
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(14)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        title = QLabel("💻🛠️ Developer Console")
        title.setStyleSheet("font-weight: 900; font-size: 15px;")
        card_layout.addWidget(title)

        # ✅ Run diagnostics button
        self.btn_diag = QPushButton("🧪 Run Diagnostics")
        self.btn_diag.setObjectName("ActionPrimary")
        self.btn_diag.setMinimumHeight(54)
        self.btn_diag.clicked.connect(self.function_btn_diagnostics)
        card_layout.addWidget(self.btn_diag)

        # ✅ Big log area
        self.dev_log = QTextEdit()
        self.dev_log.setReadOnly(True)
        self.dev_log.setLineWrapMode(QTextEdit.NoWrap)
        self.dev_log.setStyleSheet("""
            QLineEdit {
                padding: 14px 14px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.10);
                background: rgba(255,255,255,0.02);
                color: rgba(234,240,255,0.92);
                font-weight: 700;
                font-size: 13px;
            }
        """)
        self.dev_log.setFixedHeight(220)
        self.dev_log.setText("Ready. Click 'Run Diagnostics' to check paths and runtime state.")
        card_layout.addWidget(self.dev_log)

        outer.addWidget(card)
        outer.addStretch()
        return w

    def _schedule_tick(self):
        """
        매 30초마다 실행:
        - config.get_check_time() 값(0~23)과 현재 시(hour)이 같으면
        - 오늘 날짜에 아직 자동 캡쳐를 안 했을 때 program.capture() 호출
        """
        try:
            target_hour = int(config.get_check_time())  # 0~23
        except Exception:
            return

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if self._last_auto_capture_date == today:
            return

        if now.hour != target_hour:
            return

        self._run_auto_capture()

    def _run_auto_capture(self):
        self.line_status.setText("🟡 capture...")

        try:
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            program.capture_status()
            self._update_recent_capture()
            self._last_auto_capture_date = today
            self.line_status.setText("🟢 capture done")
        except Exception as e:
            self.line_status.setText(f"🔴 capture failed: {e}")

    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.header_clock.setText(f"🕒 {now}")
    def _update_recent_capture(self):
        base_title = "Recent status capture image"

        pix = QPixmap()
        ok = pix.load(path.IMG_RECENT_STATE) 

        if (not ok) or pix.isNull() or (not os.path.exists(path.IMG_RECENT_STATE)):
            self.img_title.setText(f"{base_title} (-)")
            self.dashboard_img.clear()
            self.dashboard_img.setText(f"Image not found\n{path.IMG_RECENT_STATE}")
            self.dashboard_img.setAlignment(Qt.AlignCenter)
            self.dashboard_img.setStyleSheet("""
                QLabel#ImageView {
                    background: rgba(255,255,255,0.02);
                    border: 1px solid rgba(255,255,255,0.06);
                    color: rgba(234,240,255,0.55);
                }
            """)
            return

        mtime = os.path.getmtime(path.IMG_RECENT_STATE)
        dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        self.img_title.setText(f"{base_title} ({dt})")

        self.dashboard_img.setStyleSheet("""
            QLabel#ImageView {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.06);
            }
        """)
        self.dashboard_img.setPixmap(pix)
    
    def function_btn_capture(self):
        self._run_auto_capture()
        self._update_recent_capture()
    def function_btn_maxi_node(self):
        program.maximize()
        self._raise()
    def function_btn_mini_node(self):
        program.minimize()
        self._raise()
    def function_btn_restart_node(self):
        program.restart()
        self._raise()
    def function_comboBox_select_item(self, index):
        config.set_check_time(index)
        self._last_auto_capture_date = None
        self._schedule_tick()
    def function_btn_check_status(self):
        self.line_status.setText('🟡 Checking...')
        isOk = program.checking_status()
        if isOk:
            self.line_status.setText('🟢 Mining Online')
        else:
            self.line_status.setText('🔴 Mining Offline')
        self._raise()
    def function_btn_diagnostics(self):
        try:
            parts = []
            parts.append("🧭 Diagnostics")
            parts.append(f"📌 CWD: {os.getcwd()}")

            # path 모듈에 자주 있는 값들(없을 수도 있으니 getattr로 안전하게)
            parts.append(f"🗂️ ICON: {getattr(path, 'ICON', '(none)')}")
            parts.append(f"🖼️ IMG_RECENT_STATE: {getattr(path, 'IMG_RECENT_STATE', '(none)')}")
            parts.append(f"📁 RECORD_BASE: {getattr(path, 'RECORD_BASE', '(none)')}")

            # 파일 존재 체크
            img_recent = getattr(path, 'IMG_RECENT_STATE', None)
            if img_recent:
                parts.append(f"✅ recent image exists: {os.path.exists(img_recent)}")

            # program 상태(있으면 좋고, 없으면 표시만)
            # 예: program.py에 _PROGRAM_HWND 같은 전역이 있을 수 있음
            hwnd = getattr(program, '_PROGRAM_HWND', None)
            parts.append(f"🪟 PiDesktop HWND: {hwnd}")

            # config 상태
            try:
                parts.append(f"⏰ check_time: {config.get_check_time()}")
            except:
                parts.append("⏰ check_time: (error)")

            msg = "\n".join(parts)
            self.dev_log.setText(msg)


        except Exception as e:
            self.dev_log.setText(f"❌ Diagnostics failed: {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
