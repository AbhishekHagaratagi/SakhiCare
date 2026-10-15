# SakhiCare 2.0 (ಸಖಿಕೇರ್ / सखीकेयर)

> **Empathetic, Multilingual Women’s Health Information & Care Navigation**  
> Developed for **CHAOS 2026** | **Team Nexora**  
> Physical Device Verified on **Samsung Galaxy S24 Ultra** & Desktop Web

[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python%203.12-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Capacitor](https://img.shields.io/badge/Mobile-Capacitor%208%20%2B%20Android%20SDK%2035-119EFF?logo=capacitor&logoColor=white)](https://capacitorjs.com/)
[![Ollama](https://img.shields.io/badge/Local%20AI-Ollama%20qwen2.5%3A3b-black?logo=ollama&logoColor=white)](https://ollama.ai/)
[![Gemini](https://img.shields.io/badge/Cloud%20AI-Google%20Gemini%203.8%20Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Problem Statement

Across India and global communities, millions of women navigate reproductive health challenges, menstrual irregularities, and conditions like Polycystic Ovary Syndrome (PCOS) in silence. Key barriers include:
1. **Pervasive Stigma & Discomfort:** Women frequently delay seeking care for cycle irregularity, severe pelvic pain, or hormonal changes due to privacy concerns and cultural taboos.
2. **Language Inaccessibility:** Reliable, evidence-based medical information is predominantly in technical English, leaving vernacular speakers in Kannada and Hindi underserved.
3. **Overwhelmed Healthcare Consultations:** Patients arrive at clinics anxious and unsure how to describe their timeline and symptom patterns, leading to truncated doctor visits.

---

## Our Solution

**SakhiCare** (*Sakhi* meaning trusted female friend / companion) is a privacy-first, multilingual clinical intake and health navigation tool. It allows women to express their symptoms in their own words or via structured guided categories, reviews extracted health factors with human-in-the-loop verification, provides vetted educational insights, and synthesizes a **Doctor-Ready Summary Report** exportable directly as a clinical PDF document.

SakhiCare implements a **hybrid AI architecture**:
- **Offline-First On-Device AI (Ollama `qwen2.5:3b`):** Runs 100% locally on personal hardware (accelerated via NVIDIA RTX GPU), ensuring intimate health descriptions never leave the user's device.
- **Cloud Educational Assistant (Google Gemini 3.8 Flash):** Provides compassionate, contextual explanations and answers health questions safely within non-diagnostic bounds.
- **Rule-Based Clinical Safety Floor:** Deterministic fallback ensuring critical red-flag triage guidance operates even with zero internet connectivity and no AI models loaded.

---

## Key Features

- **🌐 Trilingual Experience:** Full native UI support and free-text processing in **English**, **Kannada (ಕನ್ನಡ)**, and **Hindi (हिन्दी)**.
- **✍️ Multimodal Symptom Intake:** Free-text natural language description ("my periods are irregular and I have acne") combined with guided body-system category selectors.
- **🤝 Human-in-the-Loop Confirmation:** Extracted symptoms are transparently displayed for user review, confirmation, or removal before analysis.
- **⚡ Dual-Engine AI Intelligence:**
  - Local LLM inference via Ollama (`qwen2.5:3b`) with sub-second GPU acceleration.
  - Conversational educational assistant powered by Google Gemini (`gemini-3.8-flash`).
- **🛡️ Evidence-Based Care Triage:** Categorizes recommended next steps into *Routine Consultation*, *Consult Soon*, or *Urgent Medical Attention* based on Rotterdam Consensus and NHS/WHO criteria.
- **📄 Native PDF Generation:** Generates an official, beautifully formatted **Doctor-Ready Summary (PDF)** directly on the device using `jsPDF` and Capacitor Native Filesystem & Share sheets (no external printer required).
- **🔐 Flexible Authentication:** Live Firebase Authentication (Email/Password & Google Sign-In) alongside a one-tap **Guest Offline Demo Mode**.
- **📱 Production-Ready Android Build:** Packaged with Capacitor 8, tested and verified on physical **Samsung Galaxy S24 Ultra** hardware with full edge-to-edge layout and status bar clearance.
- **🔌 Comprehensive Connectivity Suite:** Real-time visual network indicator with an interactive Connectivity Manager supporting USB ADB reverse tunnels and Wi-Fi LAN auto-detection.

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SakhiCare Mobile & Web Client                         │
│                  (React 19 + TypeScript + Vite + Capacitor 8)               │
│                                                                             │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐ │
│  │ Multilingual Intake   │  │ Symptom Confirmation  │  │ Doctor Summary  │ │
│  │ (EN / KN / HI)        │  │ (Human-in-the-Loop)   │  │ (jsPDF Native)  │ │
│  └───────────┬───────────┘  └───────────┬───────────┘  └────────┬────────┘ │
└──────────────┼──────────────────────────┼───────────────────────┼───────────┘
               │                          │                       │
               ▼                          ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend (Port 8000)                         │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Sanitization & Pydantic Validation                                    │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                  ┌───────────────────┴───────────────────┐                  │
│                  ▼                                       ▼                  │
│     ┌────────────────────────┐              ┌────────────────────────┐      │
│     │   Local Ollama Engine  │              │    Google Gemini API   │      │
│     │  (qwen2.5:3b on CUDA)  │              │  (gemini-3.8-flash)    │      │
│     │  100% Private Offline  │              │  Contextual Education  │      │
│     └────────────────────────┘              └────────────────────────┘      │
│                  │                                       │                  │
│                  └───────────────────┬───────────────────┘                  │
│                                      ▼                                      │
│                     ┌─────────────────────────────────┐                     │
│                     │ Deterministic Clinical Baseline │                     │
│                     │  (NHS / WHO Rotterdam Fallback) │                     │
│                     └─────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript 6, Vite 8, Lucide React, jsPDF, Vanilla CSS Tokens |
| **Mobile Runtime** | Capacitor 8 (`@capacitor/android`, `@capacitor/filesystem`, `@capacitor/share`, `@capgo/capacitor-social-login`) |
| **Backend API** | Python 3.12, FastAPI 0.115, Uvicorn, Pydantic 2, HTTPX, python-dotenv |
| **AI / Machine Learning** | Ollama (`qwen2.5:3b`), Google Generative AI (`gemini-3.8-flash`, `gemini-2.5-flash`) |
| **Cloud Services** | Firebase Auth 13 (Google Identity & Email Providers) |
| **Hardware Target** | Android 14+ / One UI 6 (Samsung Galaxy S24 Ultra verified), Windows 11 Host |

---

## Repository Structure

```
D:\Pravrutti 2.O\GitHub
│
├── README.md                      # Comprehensive project documentation
├── .gitignore                     # Git ignore rules for Python, Node, Android & Secrets
├── .env.example                   # Environment configuration template
│
├── frontend/                      # React 19 + TypeScript + Capacitor frontend
│   ├── src/                       # Application screens, components, types, and styles
│   │   ├── screens/               # AuthScreen, WelcomeScreen, CheckInScreen, ReportScreen, etc.
│   │   ├── assets/                # Botanical SakhiCare vector emblems & icons
│   │   ├── firebase.ts            # Firebase Auth & Google Social Login handler
│   │   ├── types.ts               # Shared TypeScript schemas
│   │   └── index.css              # Custom responsive CSS design system (Plum & Sage)
│   ├── public/                    # Web manifest and static assets
│   ├── android/                   # Native Android Studio Capacitor project
│   │   ├── app/src/main/          # MainActivity, AndroidManifest.xml, native resources
│   │   ├── build.gradle           # Root and app Gradle build configs
│   │   └── gradle/wrapper/        # Gradle 8.13 wrapper
│   ├── package.json               # Node dependencies
│   ├── package-lock.json          # Deterministic dependency lockfile
│   ├── vite.config.ts             # Vite development & build configuration
│   └── capacitor.config.json      # Capacitor runtime configuration
│
├── backend/                       # FastAPI Python REST backend
│   ├── main.py                    # API routes, CORS, validation, and clinical fallback rules
│   ├── ai_service.py              # Ollama local inference & Google Gemini assistant integration
│   └── requirements.txt           # Python dependency specification
│
├── scripts/                       # Developer automation and evaluation tools
│   ├── start-all.ps1              # One-click launcher for FastAPI, Vite, and Ollama
│   ├── start-all.bat              # Windows batch launcher equivalent
│   ├── run_eval.py                # Automated clinical evaluation suite (10 standard test cases)
│   ├── test_real_ai_rtx5060.py    # Dual AI runtime benchmark (Ollama GPU vs Gemini)
│   ├── test_assistant_chat.py     # AI assistant conversational verification
│   ├── test_gemini.py             # Google Gemini API connectivity validator
│   └── test_ollama.py             # Ollama local LLM health and model probe
│
├── docs/                          # In-depth architectural & audit reports
│   ├── ARCHITECTURE.md            # System design and data flow specifications
│   ├── PROJECT_STATUS.md          # 90-minute CHAOS sprint milestone log
│   ├── AI_RUNTIME_AUDIT.md        # Ollama RTX 5060 & Gemini performance audit
│   ├── ANDROID_INTEGRATION.md     # Capacitor, Social Login & S24 Ultra integration details
│   ├── CLINICAL_SAFETY.md         # Non-diagnostic guardrails and ethical standards
│   ├── EVALUATION.md              # Automated evaluation methodology and results
│   ├── DEMO_GUIDE.md              # 3-minute hackathon jury presentation walkthrough
│   └── DECISIONS.md               # Architecture Decision Records (ADRs)
│
└── release/                       # Built and verified distribution artifacts
    ├── SakhiCare.apk              # Verified Android Debug APK (Samsung S24 Ultra tested)
    └── MANIFEST.sha256            # Cryptographic SHA-256 verification hash
```

---

## System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Node.js:** v18.0.0 or higher (v20+ recommended).
- **Python:** v3.10, v3.11, or v3.12.
- **JDK / Android:** Java 17 or 21, Android SDK Platform 34 or 35 (for native Android builds).
- **Local AI (Optional):** [Ollama](https://ollama.ai/) installed with model `qwen2.5:3b`.
- **Hardware Acceleration (Optional):** NVIDIA GPU with 6GB+ VRAM for sub-second local LLM inference.

---

## Installation & Setup

### 1. Clone & Configure Environment
```bash
git clone <your-repository-url>
cd SakhiCare

# Create your local environment file from template
cp .env.example .env
```
Open `.env` in your editor and provide your `GEMINI_API_KEY` (if testing the cloud assistant) and configure backend endpoints.

### 2. Backend Setup (FastAPI)
```bash
cd backend

# Create and activate Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup (React 19 + Vite)
```bash
cd ../frontend

# Install dependencies deterministically
npm ci
# (Or npm install)
```

---

## Running the Application

### Option A: One-Click Launcher (Recommended for Windows)
From the project root:
```powershell
.\scripts\start-all.ps1
```
This automatically initiates the FastAPI backend on port `8000`, the Vite dev server on port `5173`, and probes Ollama.

### Option B: Manual Startup

**Terminal 1 — FastAPI Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

**Terminal 2 — Vite Frontend:**
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Local AI Setup (Ollama)

To enable 100% private, on-device AI inference without external cloud calls:
1. Download and install [Ollama](https://ollama.ai/).
2. Pull the optimized Qwen 2.5 3B model:
   ```bash
   ollama pull qwen2.5:3b
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```
4. Verify local GPU acceleration using our benchmark script:
   ```bash
   python scripts/test_real_ai_rtx5060.py
   ```

---

## Android APK Build & Installation

### Building the APK from Source
```bash
cd frontend

# Build production web bundle
npm run build

# Synchronize web assets and plugins to Android
npx cap sync android

# Compile Debug APK via Gradle
cd android
.\gradlew.bat assembleDebug
```
The compiled artifact is generated at:
`frontend/android/app/build/outputs/apk/debug/app-debug.apk`

### Installing the Pre-built Release APK
A verified, ready-to-install build is included in this repository under `release/SakhiCare.apk`.

To install on a connected Android phone (e.g. Samsung Galaxy S24 Ultra):
```bash
# 1. Verify ADB connection
adb devices

# 2. Install APK with replace flag
adb install -r release/SakhiCare.apk

# 3. Setup USB reverse port-forwarding for backend API access
adb reverse tcp:8000 tcp:8000

# 4. Launch the application
adb shell am start -n com.sakhicare.app/.MainActivity
```

---

## Automated Testing & Evaluation

SakhiCare includes a rigorous clinical evaluation suite covering 10 diverse women's health test cases (including Kannada, Hindi, subtle cycle changes, and emergency red flags):

```bash
python scripts/run_eval.py
```

**Validated Evaluation Metrics:**
- **Symptom Extraction Precision:** Identifies normalized clinical entities from free-text.
- **Triage Accuracy:** Ensures urgent symptoms (e.g., sudden severe abdominal pain, fainting) are flagged with immediate emergency guidance.
- **Safety Boundary Adherence:** 100% compliance with non-diagnostic language rules across all models.

---

## Clinical Safety & Privacy Principles

1. **Strictly Non-Diagnostic:** SakhiCare provides health education and symptom organization. It NEVER issues medical diagnoses, prescriptions, or definitive treatment protocols.
2. **On-Device Data Sovereignty:** Personal symptom entries stay in browser `localStorage` or device memory. No personal health records are stored in external databases.
3. **Rotterdam Criteria Alignment:** Educational content on PCOS references the international Rotterdam Consensus (2003) and WHO reproductive wellness standards.
4. **Mandatory Physician Consultation:** Every report clearly emphasizes that all self-reported information must be evaluated by a licensed healthcare provider.

---

## Limitations

- **Prototype Status:** Developed as an applied innovation prototype for the CHAOS 2026 Hackathon. Not certified as a Medical Device (SaMD).
- **Google Sign-In Domain Authorization:** Web-based Google Sign-In popups require domain registration in the Firebase Console (`localhost` is authorized; custom deploy domains require manual addition).
- **Local AI Memory Requirement:** Running the local Ollama LLM requires a minimum of 4GB RAM (or dedicated GPU VRAM). If unavailable, the application gracefully transitions to the deterministic safety baseline.

---

## Team Nexora

- **Lead AI & Systems Engineer:** Team Nexora
- **Competition:** CHAOS 2026 Hackathon
- **Focus Track:** AI for Healthcare Accessibility & Multilingual Inclusivity
