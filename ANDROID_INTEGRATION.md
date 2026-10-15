# SakhiCare 2.0 — Android Mobile Integration & APK Guide
## CHAOS 2026 | Team Nexora | GPT-6 Astra

SakhiCare 2.0 has been compiled into a standalone native Android debug APK using Capacitor and the Android Gradle build toolchain with full Firebase and hardware acceleration support.

---

## 1. Verified Compiled APK Artifact

- **Output File Path:**  
  `D:\Pravrutti 2.O\frontend\android\app\build\outputs\apk\debug\app-debug.apk`
- **File Size:** `4,571,176 bytes` (~4.36 MB)
- **Application Package ID:** `com.sakhicare.app`
- **Build Timestamp:** October 15, 2026, 3:51 PM
- **Gradle Tasks Executed:** 94 actionable tasks (100% successful in 14s)
- **Target SDK:** Android 34 / 35
- **Minimum SDK:** Android 22 (Android 5.1 Lollipop+)

---

## 2. Firebase & Google Auth Configuration

- **Source:** `D:\Pravrutti 2.O\Google Auth\google-services.json`
- **Integrated Target:** `frontend/android/app/google-services.json`
- **Firebase Project ID:** `shila-6f174`
- **Project Number:** `1034087640515`
- **Registered Clients:**
  1. `app.shila.heritage` (SHILA Heritage Care)
  2. `com.sakhicare.app` (SakhiCare Companion)
- **Application Signing Certificate SHA-1:**
  `A1:93:B2:EE:2B:1C:64:B9:FA:F9:74:86:65:D0:1D:F1:CA:E7:B9:7B`
  *(Pre-registered in `google-services.json` oauth_client certificates)*

---

## 3. Installing on a Connected Android Phone

### Step 1: Connect Phone via USB
1. On your Android phone, enable **Developer Options** (tap *Build Number* 7 times in Settings -> About Phone).
2. Enable **USB Debugging**.
3. Plug the phone into the laptop via USB cable.
4. When prompted on the phone, tap **"Always allow from this computer"**.

### Step 2: Install the Debug APK
Open PowerShell or Command Prompt on your laptop:
```powershell
adb install -r "D:\Pravrutti 2.O\frontend\android\app\build\outputs\apk\debug\app-debug.apk"
```

### Step 3: Establish High-Speed USB Reverse Proxy
To allow the APK running on the phone to reach the FastAPI backend on the laptop:
```powershell
adb reverse tcp:8000 tcp:8000
```
*(Optionally forward Vite frontend dev port: `adb reverse tcp:5173 tcp:5173`)*

Now, `http://localhost:8000` inside the Android app routes directly through the USB cable to the laptop with `< 5ms` latency.

---

## 4. Wireless Wi-Fi / LAN Network Connection

If testing wirelessly on the same Wi-Fi network:
1. Current laptop Wi-Fi IPv4 address: `10.207.237.106`.
2. Inside the SakhiCare mobile app, tap the **Connection** pill in the top header.
3. Select **"Same Wi-Fi / LAN"** and enter `10.207.237.106:8000`.
4. Tap **"Test Connection"** to verify round-trip ping and AI status.
5. Tap **"Save & Apply"**.

---

## 5. Network Security & Safe Area Compliance

- `network_security_config.xml` is configured to permit development HTTP traffic on local domains (`localhost`, `127.0.0.1`, `10.0.2.2`, and LAN IPs).
- All primary screens include safe area padding (`env(safe-area-inset-bottom)`) so that navigation bars, sticky buttons, and bottom sheets never overlap content.
