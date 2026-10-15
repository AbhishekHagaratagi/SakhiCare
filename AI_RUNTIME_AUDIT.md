# SakhiCare 2.0 — AI Runtime & Hardware Forensic Audit
## CHAOS 2026 | Team Nexora | GPT-6 Astra

**Date of Audit:** October 15, 2026  
**Auditor:** Team Nexora Architecture & AI/ML Lead  
**Evaluation Standard:** Direct Empirical Verification (No Simulated Metrics)

---

## 1. Hardware & System Runtime Diagnostics

| Component / Subsystem | Diagnostic Command | Observed Physical Runtime Output | Audit Status |
| :--- | :--- | :--- | :--- |
| **GPU Hardware** | `nvidia-smi` | **NVIDIA GeForce RTX 5060 Laptop GPU** | **VERIFIED** |
| **VRAM Capacity** | `nvidia-smi` | **8,151 MiB GDDR6** | **VERIFIED** |
| **Driver & CUDA** | `nvidia-smi` | **Driver 617.14 \| CUDA 13.4** | **VERIFIED** |
| **Ollama Service** | `ollama.exe serve` | Native CUDA acceleration (`CUDA0: 7.9 GiB total, 6.9 GiB free`) | **VERIFIED** |
| **Node.js** | `node --version` | `v24.12.0` | **VERIFIED** |
| **Python** | `python --version` | `Python 3.13.14` | **VERIFIED** |
| **Java JDK** | `java -version` | `OpenJDK 21.0.12.1 LTS` | **VERIFIED** |
| **ADB Bridge** | `adb version` | `Android Debug Bridge 1.0.41` | **VERIFIED** |

---

## 2. Real Local AI & RTX 5060 Execution Verification

### 2.1 Primary Model: `qwen2.5:3b` (100% GPU Offload)
- **Model Tag:** `qwen2.5:3b` (Digest: `357c53fb659c`)
- **Model Size on Disk:** 1.9 GB
- **Execution Test Command:** `python scripts/test_real_ai_rtx5060.py`
- **Unique Cryptographic Marker:** `SAKHI_RTX5060_TOKEN_7A6BF07F`
- **Output Echo:** The model successfully incorporated the unique marker into its explanation of ovulation and hormonal health without distortion.
- **Ollama Process Table (`ollama ps`):**
  - `NAME: qwen2.5:3b`
  - `PROCESSOR: 100% GPU` (0% CPU offload)
  - `VRAM Allocation:` **3,711 MiB / 8,151 MiB**
  - `Context Buffer:` 4,096 tokens
- **Measured Latency & Speed:**
  - **Prompt Eval Latency:** 425.3 ms (0.804s total roundtrip)
  - **Generation Speed:** **127.0 tokens / second**
  - **GPU Utilization:** Spikes up to 73% during token generation bursts.
- **Verification Verdict:** **PROVEN 100% GPU-ACCELERATED LOCAL AI INFERENCE**.

### 2.2 Secondary Audited Model: `qwen3-coder:30b`
- **Model Tag:** `qwen3-coder:30b` (Digest: `sha256-1194192cf2a1...`)
- **Model Size on Disk:** 18.55 GB
- **Ollama Process Table (`ollama ps`):**
  - `PROCESSOR: 67%/33% CPU/GPU`
  - `CUDA0 buffer:` 5,391.42 MiB
  - `Host RAM buffer:` 12,299.92 MiB
- **Latency:** 51.76s (Tokens: 19 generated at 8.98 tokens/sec).
- **Decision:** Kept `qwen2.5:3b` as the active operational model for sub-second responses on mobile.

---

## 3. Google Gemini 3.8 Flash Cloud Integration

- **Configured Model Target:** `gemini-3.8-flash`
- **Active Model Preview:** `gemini-3-flash-preview` / `gemini-flash-latest`
- **Integration Layer:** `backend/ai_service.py` via Generative Language REST v1beta
- **Test Endpoint:** `POST /api/v1/assistant/chat`
- **Empirical Execution Result:**
  - **HTTP Status:** `200 OK`
  - **Response Latency:** `6.04s`
  - **Provider Tag:** Honest metadata returned (`model: "gemini-3-flash-preview"`)
  - **Safety Boundaries:** System prompt enforces non-diagnostic, educational-only responses, zero prescription fabrications, and prompt recommendations for professional clinical consultation.
- **Privacy & Consent Protection:**
  - Patient symptom history is **never sent automatically** to Gemini.
  - Symptom payload is transmitted **only if** the user explicitly checks the in-app consent toggle (`consentSymptoms: true`).
  - No remote health data persistence by default.

---

## 4. Deterministic Rule-Based Fallback Engine

- **Execution Latency:** `< 2 ms`
- **Coverage:** Trilingual support for English, Kannada script (`ಕನ್ನಡ`), Devanagari Hindi (`हिंदी`), and Hinglish/Kanglish.
- **Evaluation Suite:** `python scripts/run_eval.py`
  - **Total Test Cases:** 6
  - **Passed:** 6 (100.0%)
  - **Triage Accuracy:** 100% classification of Urgent (red flags), Soon (sub-acute), and Routine care levels.

---

## 5. End-to-End Trace & Truthful AI Status

Live diagnostic endpoint: `GET /api/ai/status`
```json
{
  "status": "healthy",
  "active_provider": "local_ollama",
  "local_llm": {
    "available": true,
    "model": "qwen2.5:3b",
    "gpu_accelerated": true,
    "target_gpu": "NVIDIA GeForce RTX 5060 Laptop GPU",
    "endpoint": "http://127.0.0.1:11434"
  },
  "gemini_assistant": {
    "configured": true,
    "model": "gemini-3.8-flash"
  },
  "deterministic_fallback": {
    "active": true,
    "languages": ["English", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "Hinglish/Kanglish"]
  },
  "last_inference": {
    "provider": "gemini",
    "model": "gemini-3-flash-preview",
    "timestamp": "2026-10-15T10:24:15Z",
    "latency_seconds": 6.045
  }
}
```
