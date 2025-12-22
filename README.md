# 🎸 Fretify

**AI-powered guitar transcription that turns any audio into accurate, interactive tablature.**

---

## Day 1 — Project Setup
**Date:** October 20, 2025  

### Summary
- Defined the project goal: creating an AI that converts guitar and bass audio into tablature.
- Named the project **Fretify**.
- Created the GitHub repository and linked it to the local project folder.
- Set up a Python virtual environment to isolate dependencies.
- Installed core libraries required for audio processing and AI development (`librosa`, `numpy`, `torch`, `demucs`, `fastapi`, etc.).
- Added a `.gitignore` file to exclude unnecessary or large files (virtual environments, cache, logs, audio data, models).
- Reviewed how virtual environments and dependency tracking work using `requirements.txt`.
- Chose technical stack: **FastAPI** (backend) + **React + TypeScript** (frontend).
- Established progressive development approach: build features incrementally as needed.
- Decided to use **basic-pitch** (Spotify) for audio transcription instead of building from scratch.
- **Created FastAPI backend structure with working health check endpoints** (`/`, `/health`, `/api/v1/info`).

### Next Steps
- Test basic-pitch with sample audio files to validate transcription quality.
- Implement MIDI → tablature conversion algorithm.
- Create file upload functionality in the backend.

---

##  Project Vision

Upload a video from TikTok, a live recording, or your own playing—Fretify analyzes it and generates complete tabs with tuning detection, finger positions, and an interactive coaching system to help you learn and improve.

---

##  Planned Features

### Phase 1 - MVP
- Upload audio (MP3, WAV, FLAC) and video files
- Audio-to-tablature transcription
- Automatic tuning detection
- Voice/instrument separation (guitar isolation)
- Save and manage generated tabs
- Interactive tab display

### Phase 2 - Enhancement
- Finger position visualization on fretboard
- Simplified version generation (beginner-friendly)
- Audio playback synced with auto-scrolling tabs
- BPM and tempo detection
- Multi-instrument support (acoustic, electric, bass)

### Phase 3 - Advanced
- Real-time coaching system
- Record and analyze your playing
- Personalized performance feedback
- Practice mode with section looping
- Export to multiple formats (PDF, Guitar Pro, TuxGuitar)
- Built-in metronome

---

##  Tech Stack

**Backend:** Python 3.11+ • FastAPI • PostgreSQL  
**Frontend:** React • TypeScript • Vite • TailwindCSS  
**AI/Audio:** basic-pitch • demucs • librosa • PyTorch  

---

## 📄 License

*To be determined*

---

