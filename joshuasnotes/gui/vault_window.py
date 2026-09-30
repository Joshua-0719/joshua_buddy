"""
Native PySide6 replica of the React/WebEngine vault UI.
Three-column layout: Sidebar | Notes list | Detail panel.
Matches the original styles.css colour palette and spacing exactly.
"""

import math
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea,
    QSizePolicy, QSplitter, QTextEdit, QVBoxLayout, QWidget,
)

# ── Colour tokens (mirrors :root in styles.css) ───────────────
PAPER   = "#ffffff"
CANVAS  = "#f5f6f4"
INK     = "#202d2b"
MUTED   = "#83908c"
LINE    = "#e7ebe8"
GREEN   = "#188779"
GREEN_S = "#e5f2ee"
SIDEBAR_BG = "#fbfcfa"

FONT = '".AppleSystemUIFont", "Helvetica Neue", sans-serif'

# ── Helpers ────────────────────────────────────────────────────
def _format_date_short(iso: str | None) -> str:
    if not iso:
        return "Just now"
    try:
        dt = datetime.fromisoformat(iso)
    except Exception:
        return iso[:10]
    today = datetime.now().date()
    if dt.date() == today:
        return dt.strftime("%-I:%M %p").lstrip("0")
    return dt.strftime("%b %-d")


def _format_date_long(iso: str | None) -> str:
    if not iso:
        return "Just captured"
    try:
        dt = datetime.fromisoformat(iso)
    except Exception:
        return iso[:16]
    return dt.strftime("%A, %B %-d, %-I:%M %p")


# ══════════════════════════════════════════════════════════════
#  Sidebar (left column)
# ══════════════════════════════════════════════════════════════
class _Sidebar(QFrame):
    def __init__(self, parent_vault):
        super().__init__()
        self.vault = parent_vault
        self.setFixedWidth(226)
        self.setStyleSheet(f"""
            _Sidebar {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {LINE};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 27, 15, 18)
        lay.setSpacing(0)

        # Brand lockup
        brand = QHBoxLayout()
        brand.setSpacing(10)
        mark = QLabel("J")
        mark.setFixedSize(31, 31)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setStyleSheet(f"""
            background: #e3f2ed; color: #0e6f62;
            font-size: 15px; font-weight: 800;
            border-radius: 10px;
        """)
        brand_text = QLabel("Joshua Notes")
        brand_text.setStyleSheet("font-size: 14px; font-weight: 750; color: #263632; letter-spacing: -0.25px;")
        brand.addWidget(mark)
        brand.addWidget(brand_text)
        brand.addStretch()
        lay.addLayout(brand)

        # Workspace label
        ws = QLabel("YOUR SPACE")
        ws.setStyleSheet("color: #687770; font-weight: 700; font-size: 9px; letter-spacing: 1.15px; margin-top: 47px; margin-bottom: 12px; padding-left: 10px;")
        lay.addWidget(ws)

        # Nav: All notes
        self.btn_all = self._nav_button("All notes")
        self.btn_all.setProperty("active", True)
        self.btn_all.clicked.connect(lambda: self.vault.set_view("all"))
        lay.addWidget(self.btn_all)

        # Nav: Starred
        self.btn_starred = self._nav_button("Starred")
        self.btn_starred.clicked.connect(lambda: self.vault.set_view("starred"))
        lay.addWidget(self.btn_starred)

        lay.addStretch()

        # Capture status box
        class ClickableFrame(QFrame):
            def __init__(self, parent_sidebar):
                super().__init__()
                self.sidebar = parent_sidebar
                self.setCursor(Qt.CursorShape.PointingHandCursor)

            def mousePressEvent(self, event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self.sidebar.vault.toggle_recording()

        self.status_box = ClickableFrame(self)
        self.status_box.setStyleSheet("""
            QFrame {
                border: 1px solid #e9eeea;
                border-radius: 9px;
                background: #fff;
                padding: 13px 11px;
            }
            QFrame:hover {
                border-color: #c6e2d8;
                background: #fbfefc;
            }
        """)
        sb_lay = QVBoxLayout(self.status_box)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(4)
        self.status_title = QLabel("Ready to capture")
        self.status_title.setStyleSheet("font-size: 10px; font-weight: 650; color: #35443f;")
        self.status_hint = QLabel("Click or hold ⌥ Space")
        self.status_hint.setStyleSheet("font-size: 9px; color: #687770;")
        sb_lay.addWidget(self.status_title)
        sb_lay.addWidget(self.status_hint)
        lay.addWidget(self.status_box)

        # Shortcut hint
        sc = QHBoxLayout()
        sc_label = QLabel("Push to talk")
        sc_label.setStyleSheet("font-size: 9px; color: #687770;")
        sc_kbd = QLabel("⌥ Space")
        sc_kbd.setStyleSheet("""
            font-size: 9px; color: #58645f;
            padding: 4px 6px;
            border: 1px solid #e5e9e6; border-radius: 5px;
            background: #fff;
        """)
        sc.addWidget(sc_label)
        sc.addStretch()
        sc.addWidget(sc_kbd)
        lay.addLayout(sc)

    def _nav_button(self, label: str) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(39)
        btn.setStyleSheet(f"""
            QPushButton {{
                border: 0; background: transparent;
                text-align: left; padding-left: 10px;
                border-radius: 7px;
                color: #697772; font-size: 11px;
            }}
            QPushButton:hover {{ background: #f0f4f1; color: #283a35; }}
            QPushButton[active="true"] {{ background: #e9f3ef; color: #147a6e; font-weight: 650; }}
        """)
        return btn

    def set_active(self, view: str):
        self.btn_all.setProperty("active", view == "all")
        self.btn_starred.setProperty("active", view == "starred")
        self.btn_all.style().unpolish(self.btn_all)
        self.btn_all.style().polish(self.btn_all)
        self.btn_starred.style().unpolish(self.btn_starred)
        self.btn_starred.style().polish(self.btn_starred)

    def update_status(self, state: str):
        mapping = {
            "recording":   ("Listening",     "Tap to finish this note"),
            "processing":  ("Transcribing",  "Tap to finish this note"),
        }
        title, hint = mapping.get(state, ("Ready to capture", "Click or hold ⌥ Space"))
        self.status_title.setText(title)
        self.status_hint.setText(hint)


# ══════════════════════════════════════════════════════════════
#  Notes column (middle)
# ══════════════════════════════════════════════════════════════
class _NoteRow(QFrame):
    """A single row in the notes list."""
    def __init__(self, note: dict, on_click, on_star):
        super().__init__()
        self.note = note
        self._on_click = on_click
        self._on_star = on_star
        self._selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(11, 12, 11, 12)
        lay.setSpacing(11)

        # Mic icon
        icon_frame = QLabel("🎙")
        icon_frame.setFixedSize(29, 29)
        icon_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_frame.setStyleSheet("""
            border: 1px solid #e6eeea; border-radius: 8px;
            background: #fff; font-size: 13px;
        """)
        lay.addWidget(icon_frame)

        # Text column
        text_col = QVBoxLayout()
        text_col.setSpacing(6)
        preview_text = note["text"].replace("\n", " ")
        if len(preview_text) > 80:
            preview_text = preview_text[:80] + "…"
        self.preview = QLabel(preview_text)
        self.preview.setWordWrap(True)
        self.preview.setStyleSheet("color: #40514b; font-size: 10px; line-height: 1.6;")

        dur = max(1, round(note.get("duration", 0)))
        meta_text = f"{_format_date_short(note.get('created_at'))}  •  {dur} sec"
        self.meta = QLabel(meta_text)
        self.meta.setStyleSheet("color: #687770; font-size: 8px;")

        text_col.addWidget(self.preview)
        text_col.addWidget(self.meta)
        lay.addLayout(text_col, 1)

        # Star button
        self.star_btn = QPushButton("★" if note.get("is_starred") else "☆")
        self.star_btn.setFixedSize(24, 24)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_star_style()
        self.star_btn.clicked.connect(lambda: self._on_star(self.note))
        lay.addWidget(self.star_btn, 0, Qt.AlignmentFlag.AlignTop)

        self._apply_bg()

    def _apply_star_style(self):
        if self.note.get("is_starred"):
            self.star_btn.setStyleSheet("border:0; background:transparent; color:#d2a34b; font-size:14px;")
        else:
            self.star_btn.setStyleSheet("border:0; background:transparent; color:#c1c9c5; font-size:14px;")

    def set_starred(self, starred: bool):
        self.note["is_starred"] = starred
        self.star_btn.setText("★" if starred else "☆")
        self._apply_star_style()

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_bg()

    def _apply_bg(self):
        if self._selected:
            self.setStyleSheet("_NoteRow { border: 1px solid #e1efea; background: #f1f7f4; border-radius: 8px; }")
        else:
            self.setStyleSheet("_NoteRow { border: 1px solid transparent; background: transparent; border-radius: 8px; }")

    def mousePressEvent(self, event):
        self._on_click(self.note)


class _NotesColumn(QFrame):
    def __init__(self, parent_vault):
        super().__init__()
        self.vault = parent_vault
        self.setStyleSheet(f"background: #fff; border-right: 1px solid {LINE};")
        self.setMinimumWidth(310)
        self.setMaximumWidth(405)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(25, 39, 25, 20)
        h_lay.setSpacing(0)

        eyebrow = QLabel("YOUR LIBRARY")
        eyebrow.setStyleSheet("color: #687770; font-weight: 700; font-size: 9px; letter-spacing: 1.15px; margin-bottom: 8px;")
        h_lay.addWidget(eyebrow)

        heading_row = QHBoxLayout()
        self.heading = QLabel("All notes.")
        self.heading.setStyleSheet("font-size: 23px; font-weight: 650; color: #23312d; letter-spacing: -0.9px;")
        heading_row.addWidget(self.heading)
        heading_row.addStretch()
        sort_btn = QLabel("Recently added ▾")
        sort_btn.setStyleSheet("color: #687770; font-size: 9px;")
        heading_row.addWidget(sort_btn)
        h_lay.addLayout(heading_row)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search your notes")
        self.search.setStyleSheet(f"""
            QLineEdit {{
                height: 37px; margin-top: 22px;
                border: 1px solid #e7ece9; border-radius: 7px;
                padding: 0 10px;
                color: #263632; font-size: 10px;
                background: transparent;
            }}
            QLineEdit:focus {{ border-color: #a5d3c9; }}
        """)
        self.search.textChanged.connect(self.vault.apply_filter)
        h_lay.addWidget(self.search)
        lay.addWidget(header)

        # List meta
        self.list_meta = QLabel("0 NOTES                                ON THIS DEVICE")
        self.list_meta.setStyleSheet("color: #687770; font-weight: 700; font-size: 8px; letter-spacing: .9px; padding: 0 25px 10px 25px;")
        lay.addWidget(self.list_meta)

        # Scrollable note list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(12, 0, 12, 15)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_container)
        lay.addWidget(self.scroll, 1)

        # Empty state
        self.empty = QWidget()
        e_lay = QVBoxLayout(self.empty)
        e_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_icon = QLabel("🎙")
        e_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_icon.setStyleSheet("font-size: 18px; background: #e9f3ef; border-radius: 13px; padding: 10px;")
        e_icon.setFixedSize(42, 42)
        e_title = QLabel("A little room to think")
        e_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_title.setStyleSheet("font-size: 11px; font-weight: 650; color: #4b5b55; margin-top: 6px;")
        e_sub = QLabel("Your spoken notes will find a home here.")
        e_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_sub.setStyleSheet("font-size: 9px; color: #687770;")
        e_lay.addWidget(e_icon, 0, Qt.AlignmentFlag.AlignCenter)
        e_lay.addWidget(e_title)
        e_lay.addWidget(e_sub)
        self.empty.hide()
        lay.addWidget(self.empty)

        self.rows: list[_NoteRow] = []

    def set_heading(self, view: str):
        self.heading.setText("Starred." if view == "starred" else "All notes.")

    def update_meta(self, count: int):
        w = "NOTE" if count == 1 else "NOTES"
        self.list_meta.setText(f"{count} {w}                                ON THIS DEVICE")

    def clear_rows(self):
        for row in self.rows:
            self.list_layout.removeWidget(row)
            row.deleteLater()
        self.rows.clear()

    def add_row(self, note: dict, at_top=False):
        row = _NoteRow(note, on_click=self.vault.select_note, on_star=self.vault.toggle_star)
        if at_top:
            self.list_layout.insertWidget(0, row)
            self.rows.insert(0, row)
        else:
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)
            self.rows.append(row)

    def set_empty(self, show: bool, query: str = "", view: str = "all"):
        self.empty.setVisible(show)
        self.scroll.setVisible(not show)


# ══════════════════════════════════════════════════════════════
#  Detail column (right)
# ══════════════════════════════════════════════════════════════
class _DetailColumn(QFrame):
    def __init__(self, parent_vault):
        super().__init__()
        self.vault = parent_vault
        self.setStyleSheet(f"background: #f8f9f7;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 31, 40, 28)
        lay.setSpacing(0)

        # Toolbar
        toolbar = QHBoxLayout()
        kind = QLabel("● VOICE NOTE")
        kind.setStyleSheet("color: #687770; font-size: 8px; font-weight: 700; letter-spacing: 1px;")
        toolbar.addWidget(kind)
        toolbar.addStretch()

        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(32, 32)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #e8ece8; border-radius: 7px;
                background: #fff; font-size: 14px;
            }
            QPushButton:hover { border-color: #cae3da; background: #f5fbf8; }
        """)
        self.copy_btn.clicked.connect(self.vault.copy_current)
        toolbar.addWidget(self.copy_btn)

        self.del_btn = QPushButton("🗑")
        self.del_btn.setFixedSize(32, 32)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #e8ece8; border-radius: 7px;
                background: #fff; font-size: 14px;
            }
            QPushButton:hover { border-color: #e8c8c4; background: #fbf2ef; }
        """)
        self.del_btn.clicked.connect(self.vault.delete_current)
        toolbar.addWidget(self.del_btn)
        lay.addLayout(toolbar)

        # Date
        self.date_label = QLabel("")
        self.date_label.setStyleSheet("color: #687770; font-size: 9px; margin-top: 55px;")
        lay.addWidget(self.date_label)

        # Transcript
        self.transcript = QLabel("")
        self.transcript.setWordWrap(True)
        self.transcript.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.transcript.setStyleSheet("""
            color: #283934; font-size: 17px; font-weight: 450;
            line-height: 195%; margin-top: 26px;
        """)
        self.transcript.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(self.transcript, 1)

        # Footer
        footer = QHBoxLayout()
        fl = QLabel("✨ Captured with Joshua Notes")
        fl.setStyleSheet("color: #687770; font-size: 8px;")
        fr = QLabel("Stored privately on this Mac")
        fr.setStyleSheet("color: #687770; font-size: 8px;")
        footer.addWidget(fl)
        footer.addStretch()
        footer.addWidget(fr)
        lay.addLayout(footer)

        # Empty state
        self.empty_state = QWidget()
        e_lay = QVBoxLayout(self.empty_state)
        e_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_icon = QLabel("🎧")
        e_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_icon.setStyleSheet("font-size: 18px; background: #e9f3ef; border-radius: 13px; padding: 10px;")
        e_icon.setFixedSize(42, 42)
        e_text = QLabel("Select a note to read it")
        e_text.setStyleSheet("font-size: 10px; color: #687770;")
        e_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_lay.addWidget(e_icon, 0, Qt.AlignmentFlag.AlignCenter)
        e_lay.addWidget(e_text)
        lay.addWidget(self.empty_state)

        self.empty_state.hide()

    def show_note(self, note: dict | None):
        if note is None:
            self.date_label.hide()
            self.transcript.hide()
            self.copy_btn.hide()
            self.del_btn.hide()
            self.empty_state.show()
            return

        self.empty_state.hide()
        self.date_label.show()
        self.transcript.show()
        self.copy_btn.show()
        self.del_btn.show()

        dur = max(1, round(note.get("duration", 0)))
        self.date_label.setText(f"🕐 {_format_date_long(note.get('created_at'))}   |   {dur} sec")
        self.transcript.setText(note["text"])


# ══════════════════════════════════════════════════════════════
#  Main VaultWindow – orchestrates the three columns
# ══════════════════════════════════════════════════════════════
class VaultWindow(QWidget):
    def __init__(self, db_manager, engine=None):
        super().__init__()
        self.db = db_manager
        self.engine = engine
        self.notes: list[dict] = []
        self.selected_note: dict | None = None
        self.current_view = "all"

        self.setWindowTitle("Joshua Notes")
        self.resize(1180, 760)
        self.setMinimumSize(760, 560)
        self.setStyleSheet(f"background: {CANVAS}; font-family: {FONT};")

        # Build three columns
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = _Sidebar(self)
        self.notes_col = _NotesColumn(self)
        self.detail_col = _DetailColumn(self)

        root.addWidget(self.sidebar)
        root.addWidget(self.notes_col, 0)
        root.addWidget(self.detail_col, 1)

        self.refresh_notes()

    # ── Data ──────────────────────────────────────────────────
    def refresh_notes(self):
        self.notes = self.db.get_all_notes()
        self._rebuild_list()

    def _visible_notes(self) -> list[dict]:
        query = self.notes_col.search.text().strip().lower()
        results = []
        for n in self.notes:
            if self.current_view == "starred" and not n.get("is_starred"):
                continue
            if query and query not in n["text"].lower():
                continue
            results.append(n)
        return results

    def _rebuild_list(self):
        self.notes_col.clear_rows()
        visible = self._visible_notes()
        for note in visible:
            self.notes_col.add_row(note)

        self.notes_col.update_meta(len(visible))
        self.notes_col.set_empty(len(visible) == 0, self.notes_col.search.text(), self.current_view)

        # Auto-select first
        if visible:
            self.select_note(visible[0])
        else:
            self.select_note(None)

    # ── Actions ───────────────────────────────────────────────
    def set_view(self, view: str):
        self.current_view = view
        self.sidebar.set_active(view)
        self.notes_col.set_heading(view)
        self._rebuild_list()

    def apply_filter(self):
        self._rebuild_list()

    def select_note(self, note: dict | None):
        self.selected_note = note
        for row in self.notes_col.rows:
            row.set_selected(note is not None and row.note["id"] == note["id"])
        self.detail_col.show_note(note)

    def toggle_star(self, note: dict):
        new_val = self.db.toggle_star(note["id"])
        note["is_starred"] = new_val
        # Update the row widget
        for row in self.notes_col.rows:
            if row.note["id"] == note["id"]:
                row.set_starred(new_val)
        # If in starred view and we just un-starred, rebuild
        if self.current_view == "starred":
            self._rebuild_list()

    def copy_current(self):
        if not self.selected_note:
            return
        QApplication.clipboard().setText(self.selected_note["text"])
        self.detail_col.copy_btn.setText("✅")
        QTimer.singleShot(1600, lambda: self.detail_col.copy_btn.setText("📋"))

    def delete_current(self):
        if not self.selected_note:
            return
        self.db.delete_note(self.selected_note["id"])
        self.notes = [n for n in self.notes if n["id"] != self.selected_note["id"]]
        self._rebuild_list()

    def add_new_note(self, note_dict: dict):
        """Called by engine.note_created signal."""
        self.notes.insert(0, note_dict)
        self.notes_col.add_row(note_dict, at_top=True)
        self.notes_col.update_meta(len(self._visible_notes()))
        self.select_note(note_dict)

    def update_status(self, state: str):
        self.sidebar.update_status(state)

    def toggle_recording(self):
        if not self.engine: return
        if self.engine._state == "recording":
            self.engine.stop_recording()
        elif self.engine._state == "idle":
            self.engine.start_recording()
