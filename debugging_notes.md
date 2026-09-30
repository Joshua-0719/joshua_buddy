# Joshua Notes Debugging Notes

## Summary

This document captures the issues encountered while getting Joshua Notes to behave as a visible, usable macOS desktop app with a working global hotkey and proper startup behavior.

## What was tried

### 1) App startup from source
- Attempted to run the app via:
  - `python -m joshuasnotes.main`
- Result: failed because the system Python environment was missing `PySide6`.
- Root cause: the active shell was not using the project virtual environment.

### 2) Project venv verification
- Attempted to run:
  - `./venv/bin/python -m joshuasnotes.main`
- Result: app started, but it printed a macOS accessibility warning.
- Root cause: `pynput` keyboard monitoring was blocked by macOS because the app was not trusted for Accessibility.

### 3) Frontend runtime crash fix
- Found app logs showing:
  - `js: Uncaught ReferenceError: AudioLines is not defined`
- Investigated `frontend/src/main.jsx`.
- Result: `AudioLines` was referenced in the UI but never imported from `lucide-react`.
- Fix: replaced it with the already-imported `Mic2` icon.

### 4) Architecture mismatch in venv
- Found that the project venv had a broken NumPy install for Apple Silicon:
  - error said `have 'arm64', need 'x86_64'`
- Root cause: the venv had an x86_64 dependency mixed into an arm64 environment.
- Fix: reinstalled NumPy using the arm64 wheel in the correct venv.

### 5) macOS Accessibility permission
- The app log showed:
  - `This process is not trusted! Input event monitoring will not be possible until it is added to accessibility clients.`
- The app was then launched after enabling Accessibility in System Settings.
- Result: the hotkey then worked correctly during a live test.
- Evidence from logs:
  - `Hotkey pressed — starting recording`
  - `Hotkey released — stopping recording`
  - transcription completed successfully

### 6) Hidden app issue (LSUIElement)
- Investigated the app bundle metadata and found that the app had been packaged as a background tray-style app.
- Root cause: the PyInstaller bundle included the macOS property `LSUIElement`, which hides the app from normal app visibility.
- Fix: removed `LSUIElement` from `WhisperFlow.spec`.

### 7) Visible-window startup attempt
- Added explicit calls to show and activate the vault window:
  - `vault.show()`
  - `vault.raise_()`
  - `vault.activateWindow()`
- Also set the window flags in `web_vault_window.py` to force a visible regular window.
- Rebuilt and reinstalled the app.
- Result: the app still did not appear visibly on the user desktop, so the hidden/background launch behavior is still not fully resolved by code alone.

### 8) Installed app verification
- Verified the installed bundle exists in:
  - `~/Applications/Joshua Notes.app`
- Verified the bundle identity and display name:
  - `CFBundleDisplayName = Joshua Notes`
- Verified the app process is running via `pgrep`.
- Observed that although the process exists, the app still does not become visible as a normal window in the desktop environment.

## Why it still seems not to be working

There are a few likely layers involved:

1. macOS app visibility behavior
- The app can be launched as a background utility, which means it runs but does not appear in the Dock or Command+Tab.
- This is consistent with certain Qt tray/app configurations and with `LSUIElement`-style behavior.

2. Hidden window behavior in Qt
- Even after removing the bundle flag, the main window may still be opening behind other windows, minimized, or not given focus properly.
- The startup sequence may be executing before the window system has fully prepared or before the app is fully trusted by macOS.

3. Accessibility + input monitoring are separate from window visibility
- The hotkey issue was a permission issue.
- The app-visibility issue is a separate behavior problem.
- The fact that the process is alive while the window is absent suggests the app is running but not being surfaced to the user in the expected way.

4. A bundled app can behave differently from the source app
- Source launches can appear one way, but packaged PyInstaller builds may behave differently under macOS security and windowing rules.
- This explains why the app started in logs yet still remained invisible on the desktop.

## Best current assessment

The app is functionally alive and the hotkey path was proven to work once Accessibility was granted. The remaining failure is that the macOS desktop app is not surfacing as a normal visible window, which strongly suggests a hidden/background-app configuration or a Qt/macOS window activation issue in the packaged build.

The project has reached the stage where the app logic is working, but the final user-facing desktop behavior still needs a macOS windowing fix rather than a backend bug fix.
