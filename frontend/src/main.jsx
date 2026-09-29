import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Check,
  ChevronDown,
  Clock3,
  Copy,
  FileText,
  Headphones,
  Mic2,
  MoreHorizontal,
  Search,
  Sparkles,
  Star,
  Trash2,
  X,
} from 'lucide-react';
import './styles.css';

function connectDesktop(setBridge, setNotes, setStatus) {
  if (!window.qt?.webChannelTransport || !window.QWebChannel) return;
  window.QWebChannel(window.qt.webChannelTransport, ({ objects }) => {
    const api = objects.desktop;
    setBridge(api);
    api.getNotes((payload) => setNotes(JSON.parse(payload)));
    api.getState(setStatus);
    api.notesChanged.connect((payload) => setNotes(JSON.parse(payload)));
    api.stateChanged.connect(setStatus);
  });
}

function formatDate(value) {
  if (!value) return 'Just now';
  const date = new Date(value);
  const today = new Date();
  const sameDay = date.toDateString() === today.toDateString();
  return sameDay
    ? date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
    : date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function formatFullDate(value) {
  if (!value) return 'Just captured';
  return new Date(value).toLocaleString([], {
    weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit',
  });
}

function App() {
  const [bridge, setBridge] = useState(null);
  const [notes, setNotes] = useState([]);
  const [status, setStatus] = useState('idle');
  const [query, setQuery] = useState('');
  const [view, setView] = useState('all');
  const [selectedId, setSelectedId] = useState(null);
  const [copied, setCopied] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => connectDesktop(setBridge, setNotes, setStatus), []);

  const visibleNotes = notes.filter((note) => {
    const matchesQuery = note.text.toLowerCase().includes(query.trim().toLowerCase());
    return matchesQuery && (view === 'all' || note.is_starred);
  });
  const selectedNote = visibleNotes.find((note) => note.id === selectedId) || visibleNotes[0] || null;

  useEffect(() => {
    if (selectedNote) setSelectedId(selectedNote.id);
  }, [selectedNote?.id]);

  const copyNote = () => {
    if (!selectedNote) return;
    if (bridge) bridge.copyText(selectedNote.text, () => {});
    else navigator.clipboard?.writeText(selectedNote.text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  const toggleStar = (event, note) => {
    event.stopPropagation();
    if (!bridge) return;
    bridge.toggleStar(note.id, (payload) => {
      const result = JSON.parse(payload);
      if (result.ok) setNotes((current) => current.map((item) => item.id === note.id
        ? { ...item, is_starred: result.is_starred }
        : item));
    });
  };

  const deleteNote = () => {
    if (!bridge || !selectedNote) return;
    bridge.deleteNote(selectedNote.id, (payload) => {
      const result = JSON.parse(payload);
      if (result.ok) setNotes((current) => current.filter((note) => note.id !== selectedNote.id));
      setMenuOpen(false);
    });
  };

  const isWorking = status === 'recording' || status === 'processing';
  const statusText = { recording: 'Listening', processing: 'Transcribing' }[status] || 'Ready to capture';
  let emptyNotesTitle = 'A little room to think';
  if (view === 'starred') emptyNotesTitle = 'No starred notes yet';
  if (query) emptyNotesTitle = 'Nothing found';

  return (
    <motion.div className="app-shell" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.35 }}>
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">J</div>
          <span>Joshua Notes</span>
        </div>

        <div className="workspace-label">YOUR SPACE</div>
        <nav className="main-nav" aria-label="Notes views">
          <button className={`nav-item ${view === 'all' ? 'active' : ''}`} onClick={() => setView('all')}>
            <FileText size={17} /><span>All notes</span><span className="nav-count">{notes.length}</span>
          </button>
          <button className={`nav-item ${view === 'starred' ? 'active' : ''}`} onClick={() => setView('starred')}>
            <Star size={17} /><span>Starred</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button className={`capture-status ${isWorking ? 'working' : ''}`} onClick={() => {
            if (!bridge || status === 'processing') return;
            if (status === 'recording') bridge.stopRecording();
            else bridge.startRecording();
          }} disabled={!bridge || status === 'processing'}>
            <span className="status-pulse" />
            <span className="status-copy"><strong>{statusText}</strong><span>{isWorking ? 'Tap to finish this note' : 'Click or hold ⌥ Space'}</span></span>
          </button>
          <div className="shortcut"><span>Push to talk</span><kbd>⌥ Space</kbd></div>
        </div>
      </aside>

      <main className="notes-column">
        <header className="notes-header">
          <div className="eyebrow">YOUR LIBRARY</div>
          <div className="heading-row">
            <h1>{view === 'starred' ? 'Starred' : 'All notes'}<span className="heading-dot">.</span></h1>
            <button className="sort-button">Recently added <ChevronDown size={14} /></button>
          </div>
          <label className="search-field">
            <Search size={17} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search your notes" />
            {query && <button aria-label="Clear search" onClick={() => setQuery('')}><X size={15} /></button>}
            {!query && <kbd>⌘ K</kbd>}
          </label>
        </header>

        <div className="list-meta"><span>{visibleNotes.length} {visibleNotes.length === 1 ? 'NOTE' : 'NOTES'}</span><span>ON THIS DEVICE</span></div>
        <div className="note-list">
          <AnimatePresence initial={false} mode="popLayout">
            {visibleNotes.map((note, index) => (
              <motion.button
                className={`note-row ${selectedNote?.id === note.id ? 'selected' : ''}`}
                key={note.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -12 }}
                transition={{ duration: 0.2, delay: Math.min(index * 0.025, 0.15) }}
                onClick={() => setSelectedId(note.id)}
              >
                <span className="note-icon"><Mic2 size={16} /></span>
                <span className="note-row-copy"><span className="note-preview">{note.text.replace(/\s+/g, ' ')}</span><span className="note-row-meta">{formatDate(note.created_at)}<i />{Math.max(1, Math.round(note.duration))} sec</span></span>
                <span className="note-row-actions">
                  <button type="button" aria-label={note.is_starred ? 'Unstar note' : 'Star note'} className={`star-control ${note.is_starred ? 'starred' : ''}`} onClick={(event) => toggleStar(event, note)}><Star size={15} /></button>
                </span>
              </motion.button>
            ))}
          </AnimatePresence>
          {visibleNotes.length === 0 && (
            <motion.div className="empty-list" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="empty-glyph"><Mic2 size={21} /></div>
              <strong>{emptyNotesTitle}</strong>
              <span>{query ? 'Try another search.' : 'Your spoken notes will find a home here.'}</span>
            </motion.div>
          )}
        </div>
      </main>

      <section className="detail-column" aria-label="Selected note">
        <AnimatePresence mode="wait">
          {selectedNote ? (
            <motion.article className="note-detail" key={selectedNote.id} initial={{ opacity: 0, y: 7 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.2 }}>
              <div className="detail-toolbar">
                <div className="detail-kind"><span className="kind-dot" /> VOICE NOTE</div>
                <div className="toolbar-actions">
                  <button className="icon-button" onClick={copyNote} aria-label="Copy transcript" title="Copy transcript">{copied ? <Check size={17} /> : <Copy size={17} />}</button>
                  <div className="menu-wrap">
                    <button className="icon-button" aria-label="More actions" title="More actions" onClick={() => setMenuOpen((open) => !open)}><MoreHorizontal size={18} /></button>
                    <AnimatePresence>{menuOpen && <motion.div className="action-menu" initial={{ opacity: 0, y: -4, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -4 }}><button onClick={deleteNote}><Trash2 size={15} /> Delete note</button></motion.div>}</AnimatePresence>
                  </div>
                </div>
              </div>
              <div className="detail-date"><Clock3 size={14} />{formatFullDate(selectedNote.created_at)}<span className="date-divider" />{Math.max(1, Math.round(selectedNote.duration))} sec</div>
              <div className="transcript-text">{selectedNote.text}</div>
              <div className="detail-footer"><span><Sparkles size={14} /> Captured with Joshua Notes</span><span>Stored privately on this Mac</span></div>
            </motion.article>
          ) : (
            <motion.div className="detail-empty" key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="empty-glyph"><Headphones size={22} /></div>
              <span>Select a note to read it</span>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </motion.div>
  );
}

createRoot(document.getElementById('root')).render(<App />);