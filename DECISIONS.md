# SakhiCare 2.0 — Architectural & Design Decisions

This document logs critical technical, clinical, and architectural decisions made during development for Team Nexora at CHAOS 2026.

---

## Decision 1: Model Selection Strategy (qwen2.5:3b vs qwen3-coder:30b)
- **Context:** The development machine had a pre-installed 18.5 GB model `qwen3-coder:30b`. On an 8 GB RTX 5060 Laptop GPU, this model required a 67% CPU / 33% GPU split, resulting in a cold latency of 51.76 seconds.
- **Decision:** Downloaded and benchmarked `qwen2.5:3b` (1.9 GB disk / 2.2 GB VRAM footprint).
- **Result:** `qwen2.5:3b` fits 100% inside the RTX 5060's GDDR6 VRAM, achieving warm inference latency of **0.47 seconds (470 ms)** at 73% GPU utilization. The backend dynamically supports both models, preferring the high-speed 3B model while falling back gracefully.

---

## Decision 2: Gemini Resilient Model Fallback Pipeline
- **Context:** `gemini-3.8-flash` is the preferred cloud assistant model, but public model endpoints can occasionally experience temporary demand spikes (HTTP 503 Service Unavailable).
- **Decision:** Implemented an automated failover loop: `["gemini-3.8-flash", "gemini-3-flash-preview", "gemini-flash-latest"]`.
- **Result:** When `gemini-3.8-flash` encountered high demand, the service seamlessly failed over to `gemini-3-flash-preview` within the same call, generating a complete, compassionate clinical response in 6.78s without user interruption.

---

## Decision 3: Zero-Retention RAM Privacy & Explicit Consent
- **Context:** Transmitting sensitive reproductive health data (menstrual cycles, fertility difficulties) to cloud AI providers presents serious privacy and compliance concerns.
- **Decision:** 
  1. The assistant operates without needing user symptoms by default.
  2. Users must explicitly toggle a consent switch (*"Share my confirmed symptoms for context"*) before symptom text is attached to external LLM prompts.
  3. No chat logs, symptoms, or identifiable profile details are persisted on backend disks or remote databases. All session data resides ephemerally in browser RAM.

---

## Decision 4: Dual-Channel Network Architecture (USB ADB + Wi-Fi LAN)
- **Context:** Physical Android devices during hackathon demos often encounter unpredictable campus Wi-Fi AP isolation or firewall blocks.
- **Decision:** Provided dual connectivity:
  - **Option A (USB / ADB Reverse):** Runs `adb reverse tcp:8000 tcp:8000`, allowing the phone to communicate over high-speed USB cable directly with the laptop's localhost without Wi-Fi dependency.
  - **Option B (Wi-Fi LAN IP):** Allows entering the laptop's LAN IPv4 address (e.g. `http://10.207.237.106:8000`) with in-app ping latency verification.
- **Result:** Guaranteed demonstrability regardless of network conditions.

---

## Decision 5: Non-Diagnostic Clinical Boundary
- **Context:** AI symptom checkers frequently face backlash for claiming diagnostic capability.
- **Decision:** Enforced a strict non-diagnostic boundary at the NLP prompt, backend rule, and UI presentation layers.
- **Result:** The system translates symptoms into structured summaries and suggested doctor questions under the Rotterdam criteria, reinforcing patient agency rather than replacing certified clinical practitioners.
