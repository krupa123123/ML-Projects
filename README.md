# 🎯 AI Communication Trainer

> *Practice technical explanations. Get AI feedback. Improve visibly.*

A personal AI-powered communication coach that transcribes speech, analyzes clarity/structure, and tracks improvement over time. Built to solve the "great work, invisible impact" problem.

---

## 🚀 Why This Exists

**Problem:** Technical people do great work but struggle to communicate it. Result: underestimated, passed over for opportunities.

**Solution:** An app that forces daily communication practice with quantified feedback. Every session creates:
- A portfolio artifact (code + demo)
- A visible improvement metric
- A LinkedIn post opportunity

---

## ✨ Features

| Feature | Tech | Purpose |
|---------|------|---------|
| 🎙️ Voice Recording | Whisper (local) + sounddevice | Transcribe speech with timestamps |
| 🤖 AI Analysis | GPT-4o-mini API | Clarity, structure, filler-word detection |
| 📊 Progress Tracking | SQLite + Matplotlib | Trend visualization over time |
| 🖥️ Dashboard | Streamlit | Zero-friction practice loop |

---

## 🛠️ Tech Stack

┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Streamlit  │────▶│  Audio Input │────▶│  Whisper (local) │
│   (UI)      │     │  (sounddevice)│     │  (transcription) │
└─────────────┘     └──────────────┘     └─────────────────┘
│                                           │
▼                                           ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  SQLite DB  │◀────│  Analyzer    │◀────│  GPT-4 API      │
│  (metrics)  │     │  (feedback)   │     │  (evaluation)   │
└─────────────┘     └──────────────┘     └─────────────────┘
