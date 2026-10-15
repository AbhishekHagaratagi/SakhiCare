# SakhiCare — Hackathon Live Demonstration & Presentation Playbook

**Team Nexora | CHAOS 2026**  
**Problem Statement:** Women's Health — Understanding Symptoms & Care Navigation (Focus on PCOS)

---

## 1. The 3-Minute Elevator Pitch

> *"Good afternoon, judges. In India, 1 in 5 reproductive-age women experiences symptoms consistent with Polycystic Ovary Syndrome (PCOS). Yet, up to 70% remain undiagnosed due to stigma, clinical jargon, and language barriers.*
>
> *Existing health apps fall into two dangerous extremes: either they serve generic, intimidating web search results, or they recklessly claim to 'diagnose' users with AI—violating clinical safety.*
>
> *We built **SakhiCare** ('Sakhi' = trusted female friend in Sanskrit, Hindi, and Kannada): a compassionate, multilingual health information and care navigation companion. It translates everyday descriptions in Kannada, Hindi, Hinglish, or English into structured, actionable understanding, grounds guidance strictly in WHO and NHS protocols, and generates a Doctor-Ready Summary to bridge the patient-provider conversation."*

---

## 2. Live Demo Script (Step-by-Step)

### Persona 1: Multilingual Regional Input (Kannada Script)
1. **Welcome Screen:**
   - Show the warm, calming interface (Deep Plum and Soft Cream palette).
   - Click **ಕನ್ನಡ** to demonstrate instant full-interface translation.
   - Point out the prominent disclosure: *"ಶೈಕ್ಷಣಿಕ ಮಾರ್ಗದರ್ಶಿ — ರೋಗನಿರ್ಣಯವಲ್ಲ"* (Educational guide, not a medical diagnosis).
2. **Check-In Screen:**
   - In the free-text box, paste:
     `ನನಗೆ ಮೂರು ತಿಂಗಳಿಂದ ಮುಟ್ಟು ಸರಿಯಾಗಿ ಬರುತ್ತಿಲ್ಲ, ಮುಖದಲ್ಲಿ ಕೂದಲು ಜಾಸ್ತಿಯಾಗಿದೆ ಮತ್ತು ಹೊಟ್ಟೆ ನೋವು ಇದೆ`
   - Select duration: **3-6 months**.
   - Click **ಮುಂದುವರಿಯಿರಿ** (Continue).
3. **Confirm Screen:**
   - Show human-in-the-loop validation: The system extracted **Irregular periods**, **Excess facial hair**, and **Pelvic pain**.
   - The user has complete control to add or remove symptoms before processing.
4. **Results Screen:**
   - **Triage status:** Routine consultation recommended.
   - **PCOS Pattern Context:** Explains why this combination is significant under the Rotterdam criteria.
   - **Interactive Tabs:** Show Care Navigation (Gynecologist, Endocrinologist, Dietitian) and Questions for the Doctor.
5. **Doctor-Ready Summary:**
   - Click **Generate Doctor-Ready Summary**.
   - Show the clean printable report with organized timeline, questions for the doctor, and clinical disclaimers.

---

### Persona 2: Urban Hinglish & Red Flag Triage
1. Switch to English / Hinglish on the Welcome screen.
2. Enter:
   `"I have sudden unbearable pelvic pain and soaking multiple pads an hour"`
3. Show the **Urgent Safety Card** trigger immediately:
   - High-visibility red alert badge.
   - Immediate guidance to seek emergency care or hospital admission.
   - Explains clinical risk without panicking the patient.

---

## 3. High-Value Judge Defense Q&A

**Q1: How do you prevent medical liability and ensure you aren't diagnosing?**  
> *"We built architectural guardrails at both the prompt and deterministic levels. The application explicitly never outputs 'You have X'. Instead, it uses evidence-based educational matching based on NHS/WHO literature. We structure symptoms for the doctor rather than replacing the doctor."*

**Q2: What if the user is in an area with poor internet connectivity?**  
> *"SakhiCare features a dual-engine architecture. If local Ollama LLMs or cloud endpoints are unreachable, our deterministic trilingual keyword engine processes queries in < 2ms entirely client/local-side without needing an active internet connection."*

**Q3: How do you handle dialectal differences across regional languages?**  
> *"We mapped both formal regional scripts (Kannada, Devanagari Hindi) and phonetically romanized colloquial terms (e.g., 'muttu sari illa', 'pet me dard', 'baal jhad rahe'). The human-in-the-loop confirmation screen ensures that if any phrase is ambiguous, the user verifies the extracted concepts before guidance is displayed."*
