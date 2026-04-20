# 30-Second Chair Stand Frailty Test

An automated computer vision system for conducting the CDC STEADI 30-Second Chair Stand Test using pose estimation.

---

## Overview

This project automates the clinical assessment of lower body strength and fall risk in older adults using MediaPipe pose estimation and OpenCV. The system guides the user step by step through a structured position verification sequence before the test begins, provides real-time visual and audio feedback during the test, and generates a CDC STEADI compliant score at the end.

---

## Features

- ✅ Automated sit-to-stand counting
- ✅ Real-time visual feedback
- ✅ Arm usage violation detection
- ✅ CDC STEADI compliant scoring
- ✅ Risk assessment generated only for successfully completed tests
- ✅ Works with standard webcam
- ✅ Automatic test start after proper seating
- ✅ On-screen cues and instructions before and during the test
- ✅ Countdown timers to guide the user
- ✅ **Two-screen instruction display** before the test (text + image guide)
- ✅ **Audible 3-2-1-GO countdown** using MP3 audio
- ✅ **Sequential 6-step position verification** before test starts
- ✅ Session history tracking across multiple runs

---

## Requirements

- Python 3.7+
- Webcam
- See `requirements.txt` for dependencies

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Sreeramyapasala/Sit-to-stand-frailty-project.git
cd Sit-to-stand-frailty-project
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Folder Structure

```
Sit-to-stand-frailty-project/
├── sit_to_stand_corrected.py     ← main program
├── merged_instruction.png        ← instruction image shown before test
├── README.md
├── requirements.txt
└── audio/
    ├── 1.mp3
    ├── 2.mp3
    ├── 3.mp3
    ├── go.mp3
    ├── instruction_sit.mp3
    └── instruction_hold.mp3
```

---

## How to Run

1. Open a terminal in your project folder.

2. Activate your virtual environment:

```bash
venv\Scripts\activate
```

3. Run the test:

```bash
python sit_to_stand_corrected.py
```

---

## Test Flow

### Step 1 — Patient Information
The terminal will ask for:
- Patient age (60–94)
- Patient gender (Male / Female)

### Step 2 — Instruction Screen
Two screens are displayed before the camera opens:
- **Screen 1:** Written 6-step instructions (stays for 15 seconds or press any key)
- **Screen 2:** Visual image guide showing correct positions (stays for 5 seconds or press any key)

### Step 3 — Position Verification (6 steps)
The system verifies each position **one by one** on the live camera feed before allowing the test to start. Each step must be held correctly for **2 seconds** to advance:

| Step | Position Checked |
|------|-----------------|
| 1 | Full body visible in camera frame |
| 2 | Sitting on edge of chair |
| 3 | One foot flat on the floor |
| 4 | One leg extended straight forward |
| 5 | One hand stacked on top of the other |
| 6 | Reaching forward toward extended foot |

A progress bar at the bottom shows which step the patient is on.

### Step 4 — Starting Position Check
After position verification, the system confirms the patient is:
- Seated correctly
- Arms crossed on chest
- Knees visible to the camera

### Step 5 — Audible Countdown
A **3-2-1-GO** countdown is shown on screen and played aloud using MP3 audio.

### Step 6 — 30-Second Test
- Stand up fully and sit back down repeatedly
- Count and remaining time are displayed on screen
- Arm usage is monitored continuously

### Step 7 — Results
- **On screen:** Result overlay with total stands, assessment, and session history
- **In terminal:** Full CDC STEADI formatted report

---

## Passing and Failing Conditions

### Passing Conditions
- User completes one or more valid sit-to-stand repetitions
- Arms remain crossed throughout the test
- User stays within the camera frame
- Test runs uninterrupted for the full 30 seconds

### Failing / Interrupted Conditions
- User uses arms for support at any point during the test
- User leaves the camera frame during the test
- Test is manually exited using the **Q** key
- Test is interrupted before completion

---

## Risk Assessment Logic

- Fall risk assessment is calculated **only when the test completes the full 30 seconds**
- If the test fails or is interrupted, no risk level is calculated or displayed
- Failed tests show: `Risk Level: N/A (Test not completed)`

This prevents incorrect fall-risk interpretation from incomplete or invalid test results.

---

## Scoring Norms (CDC STEADI)

| Age Range | Men (below average) | Women (below average) |
|-----------|--------------------|-----------------------|
| 60–64     | < 14               | < 12                  |
| 65–69     | < 12               | < 11                  |
| 70–74     | < 12               | < 10                  |
| 75–79     | < 11               | < 10                  |
| 80–84     | < 10               | < 9                   |
| 85–89     | < 8                | < 8                   |
| 90–94     | < 7                | < 4                   |

---

## Keyboard Shortcuts During Test

| Key | Action |
|-----|--------|
| `R` | Retry the test |
| `Q` | Quit the program |

---

## User Instructions

1. Sit in the middle of a sturdy chair.
2. Cross your arms on your chest (hands on opposite shoulders).
3. Keep your feet flat on the floor.
4. Follow the on-screen position verification steps before the test begins.
5. When GO is announced, stand up and sit down repeatedly for 30 seconds without using your arms.
6. If you use your arms, the test will stop and be marked as **Test Failed**.
7. Press **Q** at any time to quit.

---

## Notes

- This test is based on the **CDC STEADI 30-Second Chair Stand Test**.
- Below-average scores indicate increased fall risk.
- Ensure proper lighting and webcam positioning for accurate tracking.
- This is a screening tool only and should not be used alone to diagnose frailty or fall risk.
- Consider sharing results with a healthcare professional.

---

## Reference

CDC STEADI — Stopping Elderly Accidents, Deaths & Injuries
https://www.cdc.gov/steadi
