from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QListWidget, QListWidgetItem, QLabel, 
                               QLineEdit, QPushButton, QSplitter, QTextEdit, QFrame, QApplication)
from PySide6.QtCore import Qt

class VaultWindow(QWidget):
    """Polished two-pane main window for dictation history."""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.notes_data = {}  # Store full note dicts by ID

        self.setWindowTitle("Joshua Notes - Vault")
        self.resize(900, 640)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7f8;
                color: #172b32;
                font-family: "Montserrat", sans-serif;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d7e1e3;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #172b32;
                selection-background-color: #bce8e1;
            }
            QLineEdit:focus {
                border: 1px solid #149889;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e8e9;
                border-radius: 10px;
                outline: none;
                padding: 8px;
            }
            QListWidget::item {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 7px;
                padding: 12px;
                margin: 3px 0;
                color: #344b52;
            }
            QListWidget::item:hover {
                background-color: #f1f7f6;
            }
            QListWidget::item:selected {
                background-color: #e0f3ef;
                border: 1px solid #b7e2d9;
                color: #125d55;
            }
            QSplitter::handle {
                background-color: #dce6e7;
                width: 1px;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0e8e9;
                border-radius: 10px;
                padding: 16px;
                font-size: 14px;
                color: #243b42;
                selection-background-color: #bce8e1;
            }
            QPushButton {
                background-color: #147d72;
                border: 1px solid #147d72;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 700;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #106b62;
                border-color: #106b62;
            }
            QPushButton:pressed {
                background-color: #0d5c54;
            }
            QPushButton:disabled {
                background-color: #e6eded;
                border-color: #e6eded;
                color: #87999c;
            }
        """)

        self.init_ui()
        self.refresh_notes()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ── Top Bar (Title + Search) ──
        top_bar = QHBoxLayout()
        title = QLabel("Joshua Notes")
        title.setStyleSheet("font-size: 23px; font-weight: 700; color: #172b32;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search your notes")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.filter_notes)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.search_box)
        main_layout.addLayout(top_bar)
        
        # ── Splitter (Left: List, Right: Details) ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Pane: List
        self.notes_list = QListWidget()
        self.notes_list.setWordWrap(True)
        self.notes_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.notes_list.currentItemChanged.connect(self._on_note_selected)
        splitter.addWidget(self.notes_list)
        
        # Right Pane: Editor & Metadata
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(10)
        
        self.meta_label = QLabel("Select a note to view details")
        self.meta_label.setStyleSheet("color: #71868b; font-size: 12px; font-weight: 600;")

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)  # Read-only for now, can make editable later
        self.editor.setPlaceholderText("Full transcription will appear here...")

        # Action Bar (Copy button)
        action_bar = QHBoxLayout()
        action_bar.addStretch()
        self.copy_btn = QPushButton("Copy transcript")
        self.copy_btn.clicked.connect(self._copy_current_note)
        self.copy_btn.setEnabled(False)
        action_bar.addWidget(self.copy_btn)
        
        right_layout.addWidget(self.meta_label)
        right_layout.addWidget(self.editor)
        right_layout.addLayout(action_bar)
        
        splitter.addWidget(right_pane)
        
        # Set splitter ratio (35% left, 65% right)
        splitter.setSizes([300, 550])
        main_layout.addWidget(splitter)
        
    def refresh_notes(self):
        self.notes_list.clear()
        self.notes_data.clear()
        notes = self.db.get_all_notes()
        for note in notes:
            self._insert_note_item(note, at_top=False)
            
        if self.notes_list.count() > 0:
            self.notes_list.setCurrentRow(0)
            
    def _insert_note_item(self, note: dict, at_top: bool = True):
        note_id = note['id']
        self.notes_data[note_id] = note
        
        date_str = note['created_at'][:10] if note['created_at'] else "Today"
        preview = note['text'][:40].replace('\n', ' ') + ("..." if len(note['text']) > 40 else "")
        
        display_text = f"{date_str}\n{preview}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, note_id)
        
        if at_top:
            self.notes_list.insertItem(0, item)
            self.notes_list.setCurrentItem(item)
        else:
            self.notes_list.addItem(item)
            
    def _on_note_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if not current:
            self.editor.clear()
            self.meta_label.setText("Select a note to view details")
            self.copy_btn.setEnabled(False)
            return
            
        note_id = current.data(Qt.ItemDataRole.UserRole)
        note = self.notes_data.get(note_id)
        
        if note:
            date_str = note['created_at'][:16].replace('T', ' ') if note['created_at'] else "Unknown"
            self.meta_label.setText(f"Recorded on {date_str}  •  Duration: {note['duration']:.1f}s")
            self.editor.setText(note['text'])
            self.copy_btn.setEnabled(True)
            
    def _copy_current_note(self):
        text = self.editor.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.copy_btn.setText("Copied")
            # Reset text after 2 seconds
            import threading
            threading.Timer(2.0, lambda: self.copy_btn.setText("Copy transcript")).start()
            
    def filter_notes(self, query: str):
        query = query.lower()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            note_id = item.data(Qt.ItemDataRole.UserRole)
            note = self.notes_data.get(note_id)
            
            # Search against the full text, not just the preview
            match = note and query in note['text'].lower()
            item.setHidden(not match)
            
    def add_new_note(self, note_dict: dict):
        self._insert_note_item(note_dict, at_top=True)
