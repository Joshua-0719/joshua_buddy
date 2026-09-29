import json

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QApplication


class DesktopBridge(QObject):
    notesChanged = Signal(str)
    stateChanged = Signal(str)

    def __init__(self, db_manager, engine):
        super().__init__()
        self.db = db_manager
        self.engine = engine
        self.engine.state_changed.connect(self.stateChanged.emit)

    @Slot(result=str)
    def getNotes(self):
        return json.dumps(self.db.get_all_notes())

    @Slot(result=str)
    def getState(self):
        return self.engine._state

    @Slot(int, result=str)
    def toggleStar(self, note_id):
        is_starred = self.db.toggle_star(note_id)
        self.notesChanged.emit(json.dumps(self.db.get_all_notes()))
        return json.dumps({"ok": True, "is_starred": is_starred})

    @Slot(int, result=str)
    def deleteNote(self, note_id):
        self.db.delete_note(note_id)
        self.notesChanged.emit(json.dumps(self.db.get_all_notes()))
        return json.dumps({"ok": True})

    @Slot(str, result=bool)
    def copyText(self, text):
        QApplication.clipboard().setText(text)
        return True

    @Slot()
    def startRecording(self):
        self.engine.start_recording()

    @Slot()
    def stopRecording(self):
        self.engine.stop_recording()

    def refreshNotes(self):
        self.notesChanged.emit(json.dumps(self.db.get_all_notes()))