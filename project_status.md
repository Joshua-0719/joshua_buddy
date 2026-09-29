# Joshua's Notes: Project Status & Roadmap

**Date:** September 29, 2026  
**Status:** Local feature set is implemented and working; packaging and distribution are the next milestone.

---

## 🚀 Verified Project State

The codebase is now organized around a native macOS desktop app with a local transcription pipeline and a searchable vault. The project is no longer just a prototype; it is structured as a proper Python app with a GUI shell, database persistence, and a background dictation engine.

### ✅ Completed

#### 1) Dictation engine
- Local transcription pipeline is in place through the core engine layer.
- The app records audio, runs VAD to discard silent chunks, and sends only meaningful audio to the Whisper model.
- The transcription flow is split into a background `QThread` so the UI remains responsive while the model processes audio.
- The hotkey system listens for a global push-to-talk trigger and can start/stop recording without leaving the active app.

#### 2) Database and note persistence
- SQLite is initialized under the user application support directory for macOS.
- Notes are saved with transcription text, duration, timestamp, and soft-delete metadata.
- The vault exposes a history view that can list, search, and display notes in a GUI.

#### 3) Desktop shell and web UI
- PySide6 provides the macOS desktop shell, system tray, floating recording HUD, and Qt WebEngine host window.
- The Vault is a React interface built with Vite, Framer Motion, and Lucide icons, using a light Montserrat theme and animated note transitions.
- Qt WebChannel connects the web UI to Python for note search, starring, deletion, clipboard copy, and recording controls.
- The production frontend is built to `frontend/dist` and loaded locally by Qt WebEngine; no browser service is needed at runtime.

#### 4) App bootstrap and runtime flow
- `joshuasnotes/main.py` initializes the app, database, engine, and window components in a single startup path.
- The app continues running quietly in the tray, with the vault window open on launch so the user sees the interface immediately.

---

## 📍 Current Reality

The project is in a strong local-development state, but it is not yet a packaged user-ready macOS app.

The current app can be launched from source via:

```bash
cd frontend && npm ci && npm run build
cd ..
python -m joshuasnotes.main
```

This means:
- the project is functionally implemented,
- the core workflow exists,
- the app still depends on the local Python environment and model dependencies,
- packaging is the main missing bridge between a developer build and a polished desktop app.

---

## 🧩 Key Files in the Current Build

- `joshuasnotes/main.py` — application bootstrap and wiring
- `joshuasnotes/core/engine.py` — recording, transcription, injection, state handling
- `joshuasnotes/core/hotkey.py` — global hotkey listener
- `joshuasnotes/core/transcriber.py` — model-backed transcription implementation
- `joshuasnotes/core/vad.py` — silence trimming logic
- `joshuasnotes/core/injector.py` — paste-to-active-window behavior
- `joshuasnotes/database/db_manager.py` — note storage and retrieval
- `joshuasnotes/gui/` — Qt HUD/tray, WebChannel bridge, and WebEngine host
- `frontend/src/` — React interface and responsive styling
- `frontend/package.json` — frontend build dependencies and scripts

---

## 🗺️ Roadmap to the Next Milestone

### Phase 4: Packaging and Distribution
This is the immediate next milestone and the main step between a working app and a final product.

- [ ] Create a macOS bundle with PyInstaller or a similar packaging path.
- [ ] Include the model/runtime dependencies in the bundle so the app can run without a developer terminal session.
- [ ] Add a proper `.icns` app icon and Dock-friendly branding.
- [ ] Validate that the app launches from `/Applications` without requiring `python -m ...`.
- [ ] Add launch-at-login behavior for a smoother daily workflow.

### Phase 5: Product Polish
Once packaging is stable, the project can move into a deeper "second brain" phase.

- [ ] Context tagging by active application
- [ ] AI-assisted formatting of transcribed notes
- [ ] Optional export or backup flows for the local vault
- [ ] Better onboarding and first-run UX for model download/setup

---

## ⚠️ Known Gaps

1. The app is not yet bundled into a standalone `.app` distribution.
2. Auto-start at login has not yet been implemented.
3. First-run dependency setup and model loading should be smoother for non-technical users.
4. The project needs a packaging validation pass to confirm model assets and runtime files are included correctly.
5. The last recorded full-app session exited with a segmentation fault during the audio/VAD path; investigate this before treating the complete dictation workflow as stable. The web UI and bridge have separate smoke checks.

---

## ✅ Recommended Next Step

The next practical milestone is packaging validation, not another major feature expansion. Before adding advanced AI features, the app should be made into a real macOS application that can be launched reliably from the desktop environment.

Once that is complete, the roadmap can move cleanly into polish, AI formatting, and deeper note intelligence.
