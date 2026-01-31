import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QApplication, QWidget, QMainWindow,
    QPushButton, QLabel, QStackedWidget, QComboBox,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy
)

import config


class MainWindow(QMainWindow):
    def init_item(self):
        # init check time items
        for value in range(0, 24):
            key = f'{value:02}:00'
            self.item_check_time_key.append(key)
            self.item_check_time_value.append(value)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pi Node Manager')
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
        }
        
        /* ====== Left Sidebar ====== */
        QFrame#Sidebar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0F1A2F, stop:1 #0B1220);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        QLabel#BrandTitle {
            font-size: 18px;
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
            border: 1px solid rgba(80,160,255,0.38);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2E6AE6,
                        stop:1 #00BFE0);
            font-weight: 900;
            letter-spacing: 0.2px;
        }
        QPushButton#ActionPrimary:hover {
            border: 1px solid rgba(120,200,255,0.55);
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
            border: 1px solid rgba(255,255,255,0.10);
            background: #141C2B;
            font-weight: 800;
        }
        QPushButton#ActionSecondary:hover {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.16);
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
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 34px;
            border-left: 1px solid rgba(255,255,255,0.08);
            border-top-right-radius: 14px;
            border-bottom-right-radius: 14px;
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

        sub = QLabel("Minimal control panel • Dark mode UI")
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
        btn_dashboard.setChecked(True)  # default page = Dashboard

        left_layout.addWidget(brand)
        left_layout.addSpacing(6)
        left_layout.addWidget(btn_dashboard)
        left_layout.addWidget(btn_setting)
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
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(6, 2, 6, 2)
        header_layout.setSpacing(2)

        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("PageTitle")

        self.header_hint = QLabel("Quick actions for Managing")
        self.header_hint.setObjectName("PageHint")

        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_hint)

        # ---- pages
        self.pages = QStackedWidget()
        self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pages.addWidget(self.page_main())
        self.pages.addWidget(self.page_settings())

        content_layout.addWidget(header)
        content_layout.addWidget(self.pages, 1)

        # ---- signals (keep existing behavior)
        btn_dashboard.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        btn_setting.clicked.connect(lambda: self.pages.setCurrentIndex(1))

        # ✅ ensure checked highlight follows navigation
        btn_dashboard.clicked.connect(lambda: btn_dashboard.setChecked(True))
        btn_setting.clicked.connect(lambda: btn_setting.setChecked(True))

        # (UI only) Update header text on navigation (does not change any existing functions)
        btn_dashboard.clicked.connect(lambda: self._set_header("Dashboard", "Quick actions for capture / open / restart."))
        btn_setting.clicked.connect(lambda: self._set_header("Setting", "Set the daily checking time."))

        # ---------- layout ----------
        root_layout.addWidget(left)
        root_layout.addWidget(content_shell, 1)

        self.setCentralWidget(root)

    # (UI helper only)
    def _set_header(self, t, h):
        self.header_title.setText(t)
        self.header_hint.setText(h)

    # (UI helper only)
    def _shadow(self, widget, blur=24, y=10):
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(blur)
        eff.setOffset(0, y)
        eff.setColor(Qt.black)
        widget.setGraphicsEffect(eff)

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
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(12)

        # Big primary button
        btn_capture = QPushButton('📸  CAPTURE\nMining state')
        btn_capture.setObjectName("ActionPrimary")
        btn_capture.setMinimumHeight(92)
        btn_capture.clicked.connect(self.function_btn_capture)

        # Secondary buttons (same functions)
        btn_open_node = QPushButton('🟢  OPEN\nPi node')
        btn_open_node.setObjectName("ActionSecondary")
        btn_open_node.setMinimumHeight(92)
        btn_open_node.clicked.connect(self.function_btn_open_node)

        btn_restart_node = QPushButton('🔁  RESTART\nPi node')
        btn_restart_node.setObjectName("ActionSecondary")
        btn_restart_node.setMinimumHeight(92)
        btn_restart_node.clicked.connect(self.function_btn_restart_node)

        # proportions: primary bigger
        btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_open_node.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_restart_node.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        top_row_layout.addWidget(btn_capture, 2)
        top_row_layout.addWidget(btn_open_node, 1)
        top_row_layout.addWidget(btn_restart_node, 1)

        # Info strip (purely UI)
        info = QFrame()
        info.setStyleSheet("background: transparent; border: none;")
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(10)

        hint = QLabel("● Tip: Capture first, then restart if the node looks stuck.")
        hint.setStyleSheet("color: rgba(234,240,255,0.75); font-weight: 700;")
        info_layout.addWidget(hint)
        info_layout.addStretch()

        card_layout.addWidget(top_row)
        card_layout.addWidget(info)

        outer.addWidget(card)
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

        msg = QLabel("● Tip: Saved instantly when you change the value.")
        msg.setStyleSheet("color: rgba(234,240,255,0.75); font-weight: 700;")
        tip_layout.addWidget(msg)
        tip_layout.addStretch()

        card_layout.addSpacing(10)
        card_layout.addWidget(tip)

        outer.addWidget(card)
        outer.addStretch()

        return w

    def function_btn_capture(self):
        print('function_btn_capture')

    def function_btn_open_node(self):
        print('function_btn_open_node')

    def function_btn_restart_node(self):
        print('function_btn_restart_node')

    def function_comboBox_select_item(self, index):
        print(f'function_comboBox_select_item {index}')
        config.set_check_time(index)


if __name__ == "__main__":
    config.init()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
