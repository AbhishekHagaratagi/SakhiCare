# SakhiCare — Clinical Safety & Ethical Framework

SakhiCare adheres to clinical safety principles aligned with the National Health Service (NHS), World Health Organization (WHO), American College of Obstetricians and Gynecologists (ACOG), and the Rotterdam International PCOS Consensus Guidelines.

---

## 1. Non-Diagnostic Boundary Defense

The cardinal rule of SakhiCare is: **Do Not Diagnose.**

Women's health symptoms—especially menstrual irregularity, pelvic pain, weight fluctuation, and dermatological changes—have multifaceted etiologies including:
- Polycystic Ovary Syndrome (PCOS)
- Hypothalamic amenorrhea
- Thyroid dysfunction (hypothyroidism / hyperthyroidism)
- Endometriosis & adenomyosis
- Hyperprolactinemia
- Premature ovarian insufficiency (POI)

Presenting a statistical or algorithmic classification as a "diagnosis" exposes patients to diagnostic overshadowing, anxiety, and inappropriate self-treatment.

### Implementation Guardrails:
1. **Linguistic Framing:**
   - Forbidden: *"You have PCOS"*, *"Your diagnosis is"*, *"You are suffering from"*.
   - Required: *"When these symptoms appear together, doctors commonly evaluate for conditions like PCOS"*, *"Symptoms you reported may warrant evaluation by a healthcare provider"*.
2. **Mandatory Disclaimers:** Visible on every screen and stamped onto every printed report.
3. **Doctor-in-the-Loop:** Every workflow terminates in a doctor-ready consultation preparation guide.

---

## 2. Clinical PCOS Knowledge Base & The Rotterdam Criteria

Under the 2003 Rotterdam Consensus (reaffirmed in the 2023 International Evidence-Based PCOS Guidelines), a clinical diagnosis of PCOS requires at least **two of the following three features**, with exclusion of other etiologies:
1. **Ovulatory Dysfunction:** Oligo-ovulation or anovulation (manifesting as irregular, infrequent, or absent periods).
2. **Hyperandrogenism:** Biochemical (elevated testosterone/androstenedione) or clinical (excess facial/body hair, severe persistent cystic acne, androgenic alopecia).
3. **Polycystic Ovaries:** Polycystic morphology on pelvic ultrasound (≥20 follicles per ovary or ovarian volume ≥10 ml).

SakhiCare maps patient-reported vernacular descriptions into these clinical pillars:

| Patient Expression (Vernacular) | Clinical Symptom ID | Rotterdam / Clinical Pillar |
| :--- | :--- | :--- |
| "Periods irregular", "ಮುಟ್ಟು ಸರಿಯಾಗಿಲ್ಲ", "माहवारी लेट" | `irregular_periods` | Ovulatory Dysfunction |
| "Periods missed", "ಮುಟ್ಟು ಬರುತ್ತಿಲ್ಲ", "पीरियड नहीं आ रहे" | `missed_periods` | Ovulatory Dysfunction |
| "Facial hair", "ಮುಖದಲ್ಲಿ ಕೂದಲು", "चेहरे पर बाल" | `excess_hair` | Clinical Hyperandrogenism |
| "Stubborn cystic acne", "ಮೊಡವೆ", "पिंपल" | `acne` | Clinical Hyperandrogenism |
| "Hair thinning", "ಕೂದಲು ಉದುರುವುದು", "बाल झड़ना" | `hair_thinning` | Clinical Hyperandrogenism |
| "Weight gain", "ತೂಕ ಏರಿಕೆ", "वजन बढ़ना" | `weight_gain` | Metabolic / Insulin Resistance |
| "Pelvic discomfort", "ಹೊಟ್ಟೆ ನೋವು", "पेट दर्द" | `pelvic_pain` | Pelvic / Structural Symptom |

---

## 3. Three-Tier Safety Triage Protocol

SakhiCare implements a deterministic safety triage classifier to ensure acute medical emergencies are never downplayed:

### Tier 1: Urgent (Immediate Medical Attention Required)
- **Triggers:** Sudden unbearable pelvic pain, soaking ≥2 pads per hour for consecutive hours, fainting/dizziness with bleeding, suspected ectopic pregnancy, severe shortness of breath.
- **Guidance:** Recommends emergency department or immediate gynecological hospital admission.
- **Source:** NHS Urgent Bleeding and Pelvic Pain Protocols.

### Tier 2: Soon (Appointment Within 1–2 Weeks)
- **Triggers:** Difficulty conceiving for >12 months, absence of menses for >3 consecutive months without known cause, chronic pelvic pain, persistent bleeding between periods.
- **Guidance:** Advises scheduling a dedicated appointment with a gynecologist or reproductive endocrinologist.
- **Source:** NICE Guidelines for Infertility and Menstrual Disturbance.

### Tier 3: Routine (Next Planned Consultation)
- **Triggers:** Isolated or chronic mild cycle irregularities, gradual weight changes, mild acne or cosmetic concerns.
- **Guidance:** Recommends discussing at the patient's next primary care or wellness visit, accompanied by symptom tracking.

---

## 4. Evidence-Based Clinical Sources

All educational materials in SakhiCare link directly to verified public health authorities:
- **NHS Irregular Periods:** https://www.nhs.uk/conditions/irregular-periods/
- **NHS Polycystic Ovary Syndrome:** https://www.nhs.uk/conditions/polycystic-ovary-syndrome-pcos/
- **NHS Hirsutism (Excess Hair):** https://www.nhs.uk/conditions/hirsutism/
- **WHO Guidelines on Infertility & Reproductive Wellness:** https://www.who.int/news-room/fact-sheets/detail/infertility
- **ICMR Indian PCOS Taskforce Data:** Epidemiological data documenting 10–22% prevalence in Indian cohorts.
