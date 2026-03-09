# PhonoEcho

PhonoEcho is a Streamlit application for English pronunciation training with multimodal feedback. It combines:
- lesson content (text + video),
- learner microphone recording,
- Azure Speech pronunciation assessment,
- visual analytics (radar chart, waveform, error breakdown, score trends),
- optional AI feedback (Azure OpenAI / Gemini),
- optional haptic synchronization support (bHaptics TactGlove).

![human interface](interface.png)

## 1. Project Introduction

### What PhonoEcho does
PhonoEcho supports a repeatable lesson practice loop:
1. User logs in and selects a lesson.
2. The app displays lesson text and learning video.
3. The learner records speech in the browser.
4. Azure Speech returns pronunciation scores and detailed error metadata.
5. The app visualizes scores and error types.
6. Results are saved into per-user local history JSON files.
7. Optional AI feedback is generated from current error patterns.

### Scope of this repository
This repository is the main Streamlit implementation centered on:
- account and session management (`app/echo_app.py`, `app/user.py`),
- lesson/data loading (`app/dataset.py`),
- pronunciation assessment + visualization (`app/learn/echo_learning.py`),
- optional AI feedback helpers (`app/ai_chat.py`, `app/gemini_chat.py`),
- optional haptics integration (`bhaptics/`, `tact_files/`).

## 2. Local Deployment (Conda + `environment.yml`)

### Prerequisites
- Conda (Miniconda or Anaconda)
- Browser with microphone permission
- Azure Speech resource (required for pronunciation scoring)
- Optional: Azure OpenAI and/or Gemini API keys
- Optional: bHaptics setup for tactile feedback

### Important note about `environment.yml`
Current `environment.yml` is encoded as **UTF-16 LE**. If your Conda setup expects UTF-8, convert first:

```bash
# Linux/macOS
iconv -f UTF-16LE -t UTF-8 environment.yml > environment.utf8.yml
conda env create -f environment.utf8.yml
```

```powershell
# Windows PowerShell
Get-Content .\environment.yml | Set-Content -Encoding utf8 .\environment.utf8.yml
conda env create -f .\environment.utf8.yml
```

If UTF-16 works directly in your environment:

```bash
conda env create -f environment.yml
```

### Create and activate environment

```bash
conda env create -f environment.yml
conda activate phonoecho
```

### Secrets configuration
Create `.streamlit/secrets.toml` with the following structure:

```toml
[Azure_Speech]
SPEECH_KEY = "..."
SPEECH_REGION = "..."

[AzureGPT]
AZURE_OPENAI_ENDPOINT = "..."
AZURE_OPENAI_API_KEY = "..."

[Gemini]
GOOGLE_API_KEY = "..."

[Azure_Avatar]
SPEECH_ENDPOINT = "..."
SUBSCRIPTION_KEY = "..."
```

Notes:
- Azure Speech is required for assessment flow.
- Azure OpenAI and Gemini are optional.
- Azure Avatar is only needed if you use avatar synthesis tooling.

### Run app

```bash
streamlit run app/echo_app.py
```

## 3. File Hierarchy and File Guide

```text
PhonoEcho/
├─ app/
│  ├─ echo_app.py                 # Main Streamlit entry, auth navigation
│  ├─ user.py                     # User model, password hashing, history paths
│  ├─ dataset.py                  # Lesson text/video discovery by user
│  ├─ ai_chat.py                  # Azure OpenAI feedback helper
│  ├─ gemini_chat.py              # Gemini feedback helper/demo
│  ├─ elicited_imitation.py       # Elicited imitation task page
│  ├─ learn_st.py                 # Recording/waveform demo page
│  ├─ learn/
│  │  ├─ echo_learning.py         # Core learning + scoring + chart workflow
│  │  ├─ report.py                # Batch report for saved JSON results
│  │  ├─ async_haptic_integration.py
│  │  └─ ...
│  ├─ account/                    # Legacy/demo account pages
│  └─ tools/                      # Utility tools (radar/tts/avatar/etc.)
├─ bhaptics/                      # bHaptics player integration
├─ tact_files/                    # TactGlove patterns and converter
├─ logo/                          # Project logos and animation assets
├─ resources/                     # Supporting media and reference resources
├─ database/
│  ├─ all_users/users_info.json   # Registered user credentials metadata
│  ├─ learning_database/<user>/   # Lesson text/video plus optional configs
│  └─ <user>/practice_history/    # Per-day saved assessment history
├─ environment.yml
└─ README.md
```

### Core files (details)
- `app/echo_app.py`
  - Handles login/register/logout pages and sidebar navigation.
  - Routes authenticated users to the learning page.
- `app/user.py`
  - Registers/logins users with bcrypt-hashed passwords.
  - Creates user directories and saves practice history JSON files.
- `app/dataset.py`
  - Loads lesson `.txt` and `.mp4` assets from `database/learning_database/<user>/`.
- `app/learn/echo_learning.py`
  - Runs recording, Azure pronunciation assessment, score/error aggregation, and visualization.
  - Stores attempt results and lesson-level score/error history.

## 4. Data Layout

```text
database/
  all_users/
    users_info.json
  learning_database/
    <user_name>/
      *.txt
      *.mp4
      tactglove_config.json   # optional for haptic mode
  <user_name>/
    practice_history/
      YYYY-MM-DD/
        <lesson>-<timestamp>.json
        scores/
          lesson_scores.json
          error_history.json
```

## 5. Additional Notes

### Operational assumptions
- `database/all_users/users_info.json` exists before first run.
- Lesson files under `database/learning_database/<user>/` follow consistent naming.
- Browser microphone permission is enabled.
- For haptic mode, `tactglove_config.json` and compatible bHaptics setup are required.

### Troubleshooting
- App fails at startup:
  - Verify `.streamlit/secrets.toml` keys.
  - Confirm Conda env is active and dependencies are installed.
- Login works but lessons are empty:
  - Check files under `database/learning_database/<user>/`.
- Recording works but no pronunciation score appears:
  - Recheck Azure Speech key/region and connectivity.
- AI feedback missing:
  - Recheck Azure OpenAI or Gemini API settings.

## 6. Recommended Development Workflow
1. Activate the Conda environment.
2. Run `streamlit run app/echo_app.py`.
3. Validate one full attempt (record -> assess -> charts -> history save).
4. Use `app/learn/report.py` to inspect historical JSON output if needed.

## License
No license file is currently included in this repository.
