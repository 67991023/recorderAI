# RecorderAI 🎙️

**Voice Analytics Dashboard** – Record, transcribe, and cluster your speech data with K-Means AI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Real-time Recording** | Start/stop audio recording with live waveform visualisation |
| 🤖 **Speech-to-Text** | In-browser STT via Web Speech API (Thai 🇹🇭 & English 🇺🇸) |
| 🔬 **K-Means Clustering** | Automatically group recordings by word/character count patterns |
| ✅ **Flexible Selection** | Select individual recordings or analyse all at once |
| 📊 **Interactive Charts** | Scatter plot + doughnut chart powered by Chart.js |
| 🌙 **Professional Dark UI** | Slate/blue professional dark theme |
| 🐳 **Docker-ready** | One-command startup with Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)

### Run

```bash
git clone https://github.com/67991023/recorderAI.git
cd recorderAI

docker compose up
```

Open **http://localhost:8080** in Chrome or Edge.

> ⚠️ Speech-to-Text requires **Chrome** or **Edge** (Web Speech API). Firefox is not supported.

---

## 📁 Project Structure

```
recorderAI/
├── api/
│   ├── app.py                  # Flask REST API
│   ├── kmeans_service.py       # K-Means clustering logic
│   ├── test_data.py            # Demo dataset (no DB required)
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Dashboard UI
│   ├── styles.css              # Professional dark theme
│   ├── dashboard.js            # Main UI logic
│   ├── api.js                  # API client
│   ├── charts.js               # Chart.js helpers
│   ├── recorder.js             # Audio recording + waveform
│   └── transcriber.js          # Web Speech API (STT)
├── database/
│   └── init.sql                # PostgreSQL schema + seed data
└── docker-compose.yml
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/health` | Health check |
| `GET`  | `/api/recordings` | List all recordings |
| `POST` | `/api/recordings` | Create a recording `{ text, word_count }` |
| `GET`  | `/api/statistics` | Aggregate stats (count, avg/max/min words) |
| `POST` | `/api/analyze` | Cluster recordings (optional body: `{ recordings: [...] }`) |
| `POST` | `/api/analyze-selected` | Cluster by IDs `{ ids: [1, 3, 5] }` |
| `POST` | `/api/analyze-all` | Cluster all recordings |
| `GET`  | `/api/clusters` | Get latest cluster results |
| `GET`  | `/api/cluster-stats` | Detailed cluster statistics |
| `GET`  | `/api/demo-clusters` | Pre-computed demo data (no DB needed) |
| `POST` | `/api/recordings/{id}/analyze` | Analyse a single recording |
| `GET`  | `/api/recordings/{id}/transcribe` | Get stored transcription text |

---

## 🎯 Usage Guide

### 1. Record Audio
1. Click **🔴 Start Recording** – allow microphone access
2. Speak your content – the waveform visualiser shows live audio
3. Click **⏹ Stop** – the recording is saved in memory
4. Click **▶ Play** to review the audio

### 2. Transcribe Speech
1. Select language (**Thai** or **English**)
2. Click **🎤 Start Transcribe**
3. Speak – text appears in real-time in the text field
4. Click **⏹ Stop STT**
5. Adjust the text if needed and click **💾 Save Recording**

### 3. Clustering Analysis
1. On the **Dashboard** tab, check the boxes next to recordings you want to analyse
2. Click **🎯 Analyze Selected**, or use the **Clustering** tab for batch options:
   - **▶ Analyze All** – cluster every recording
   - **🎯 Analyze Selected** – cluster only your checked recordings
   - **🎬 Load Demo Data** – instant pre-computed example

---

## 🏗️ Architecture

```
Browser (port 8080)
  └── Nginx (static files)
        └── /api/* → Flask API (port 5000)
                      └── PostgreSQL (port 5432)
```

---

## 🌐 Thai Language Support

RecorderAI supports Thai (ภาษาไทย) at every level:
- STT transcription in Thai via Web Speech API (`th-TH`)
- Thai text stored and clustered by word count features
- Sample data includes Thai sentences in the demo dataset
