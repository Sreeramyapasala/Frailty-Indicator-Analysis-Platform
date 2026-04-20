# Sit-to-Stand Frailty Assessment System

**Sree Ramya Pasala** | Masters in Data Analytics Engineer

---

## [January 20–23, 2026] - Week 1

### Summary
The first week was dedicated to project onboarding and establishing a foundational understanding of the Sit-to-Stand Frailty Assessment System. Rather than beginning implementation prematurely, the focus was placed on comprehending the system architecture, stakeholder expectations, and the broader clinical context underpinning the project.

### Work Done

- **Project Onboarding:** Received and reviewed onboarding materials and task specifications from the supervisor.
  - Attended project kickoff meeting on January 22 to clarify workflow expectations and deliverable timelines.

- **Repository Review:** Conducted a thorough review of the project repository and existing Sit-to-Stand test implementation.
  - Identified the system's core mechanism: webcam-based computer vision for automated test execution.

- **Research Tasks Scoped:** Reviewed assigned research areas.
  - CDC STEADI chair stand test protocols
  - Age-group score interpretation
  - Current system limitations and improvement opportunities

### What I Learned

- Acquired foundational knowledge of frailty assessment methodologies and the clinical significance of the Sit-to-Stand test in geriatric health screening.
- Understood how computer vision techniques are applied to automate physical performance test scoring.
- Recognized the critical role of interpretable, user-facing result outputs in health-oriented software systems.

### Challenges

- Navigating an unfamiliar codebase while simultaneously learning domain-specific health concepts required careful time management and structured note-taking.
- Bridging the gap between clinical standards (CDC STEADI) and their practical representation in software logic presented an initial conceptual challenge.

### To Do (Next Steps)

- [ ] Initiate in-depth research on CDC STEADI scoring guidelines and age-stratified result interpretation
- [ ] Draft a preliminary design for the result interpretation and messaging component
- [ ] Investigate data storage options for retaining test results across sessions

---

## [January 26–30, 2026] - Week 2

### Summary
This week focused on structured research into the CDC STEADI 30-Second Chair Stand Test, culminating in a documentation artefact that translated clinical scoring standards into actionable system-level requirements. Deliverables were shared with the supervisor via GitHub and reviewed in a mid-week meeting.

### Work Done

- **CDC STEADI Research:** Conducted a comprehensive review of guidelines for the 30-second chair stand test.
  - Covered age- and gender-stratified normative score ranges
  - Identified critical system limitation: a single test metric is insufficient for robust fall-risk assessment and must be contextualized with additional health indicators

- **Documentation Artefact Produced:** Created a structured reference document comprising:
  - Age-based scoring benchmarks
  - Caution conditions for edge-case result interpretation
  - Recommended supplementary data points for future improvement

- **Result Summary Feature Proposed:** Designed a plain-text result summary generation feature to translate raw scores into user-comprehensible output.

- **Deliverables Shared:** Uploaded work to GitHub and communicated progress to the supervisor in advance of the January 28 meeting.

### What I Learned

- Gained a nuanced understanding of age-specific scoring in health data interpretation and the limitations of single-metric assessment tools.
- Developed skills in translating technical output into clinically appropriate, user-friendly summaries aligned with health informatics best practices.

### Challenges

- Interpreting CDC medical guidelines in sufficient depth to derive meaningful software requirements demanded careful cross-referencing of clinical literature.
- Ensuring that proposed system improvements remained practically implementable rather than purely theoretical required continuous alignment with the existing architecture.

### To Do (Next Steps)

- [ ] Begin integrating result summary generation logic into the system output pipeline
- [ ] Explore storing contextual patient data (fall history, balance scores) alongside test results
- [ ] Improve usability and reliability of the result display module

---

## [February 2–8, 2026] - Week 3

### Summary
Week three marked a transition from independent research into collaborative development. Engagement with the teammate who built the base Sit-to-Stand system provided critical architectural insight and enabled a more targeted approach to the result messaging contribution.

### Work Done

- **Technical Sync with Teammate:** Attended a discussion session on February 4 to understand the existing implementation, state machine logic, and identified improvement areas.

- **Integration Planning:** Mapped the result messaging feature onto specific system components to determine integration points.
  - Revisited prior research and aligned findings with actual system behaviour and constraints
  - Planned architecture for integrating plain-language result summaries into the test completion workflow

- **Responsibility Division Established:**
  - Teammate -> UX and visual interface
  - Self -> result messaging and output interpretation logic

### What I Learned

- Developed proficiency in reading and reasoning about unfamiliar codebases, particularly event-driven systems with multi-stage validation logic.
- Understood the interdependencies between UI rendering, state management, and output logic in the existing system.
- Recognized the importance of collaborative knowledge transfer when modifying established software systems.

### Challenges

- Navigating another developer's architectural decisions required significant reverse-engineering effort before implementation planning could begin.
- Mapping abstract research recommendations onto concrete, integration-ready features presented non-trivial design challenges.

### To Do (Next Steps)

- [ ] Implement result summary generation logic within the identified system components
- [ ] Ensure cross-platform compatibility of the output module
- [ ] Validate messaging logic across diverse age and score scenarios

---

## [February 9–13, 2026] - Week 4

### Summary
This week involved consolidating role clarity and preparing for implementation. While active development was minimal, the week served an important organizational function - ensuring contribution boundaries were well-defined and implementation plans were aligned with project expectations.

### Work Done

- **Role Confirmation:** Reviewed and confirmed role assignment, formally taking ownership of the result messaging and interpretation component.

- **Implementation Planning:** Defined expected behaviour and edge cases for user-facing output messages across different test outcomes.
  - Prepared an implementation plan for the messaging module
  - Ensured alignment with the broader system architecture

### What I Learned

- Appreciated the importance of explicit role delineation in team-based software projects to minimize duplication and integration conflicts.
- Understood how separating UX concerns from business logic leads to more maintainable and testable system design.

### Challenges

- Balancing the need for thorough planning against the risk of over-engineering a relatively bounded feature required careful scope management.

### To Do (Next Steps)

- [ ] Begin implementation of the result messaging module
- [ ] Validate messaging outputs with the teammate to ensure consistency with the UX layer

---

## [February 16–20, 2026] - Week 5

### Summary
Development accelerated this week with the implementation of a cross-platform text-to-speech (TTS) system, addressing a critical dependency issue with the prior Windows-only audio architecture. This work directly expanded the deployment viability of the application.

### Added

- **Cross-Platform TTS System:** Developed `tts_final.py` - a complete MP3-based TTS implementation.
  - **Voice:** TTSMaker neural voice, consistent American female tone throughout
  - **Countdown audio:** `3.mp3`, `2.mp3`, `1.mp3`, `go.mp3`
  - **Instruction audio:** `instruction_sit.mp3`, `instruction_extend.mp3`, `instruction_hold.mp3`, `instruction_relax.mp3`
  - **Storage:** 92 KB total - well within the 100 KB project constraint
  - **Cost:** $0 - fully free solution
  - **Compatibility:** Pure MP3 playback works on Mac, Windows, and Linux

### Changed

- **TTS Architecture:** Replaced Windows-only `win32com.client` SpeechManager with `FullMP3TTS` class.
  - **Rationale:** Eliminates platform-specific dependency, enables cross-platform deployment from a single codebase
  - **Benefit:** Consistent voice quality for both countdown and instruction audio

### What I Learned

- Gained practical experience evaluating TTS libraries (`pyttsx3`, `gTTS`, Web Speech API) against cross-platform, quality, and cost constraints.
- Learned that dependency isolation - pre-generated MP3s vs. runtime synthesis - can significantly improve deployment portability.

### Challenges

- Ensuring audio/visual synchronization between MP3 playback and the OpenCV video countdown required careful timing logic to prevent desynchronization.

### To Do (Next Steps)

- [ ] Integrate TTS system fully into the main Jupyter notebook
- [ ] Synchronize audio playback with visual countdown overlays in the camera feed

---

## [February 23–27, 2026] - Week 6

### Summary
This week focused on full integration of the TTS system into the primary notebook and implementing the video countdown overlay. A number of cross-platform compatibility issues were resolved, advancing the system toward a stable, end-to-end functional state.

### Added

- **Full End-to-End Test Verified:** Complete test run confirmed working.
  - All 7 pipeline stages passed: `FULL_BODY_DETECTION` -> `SITTING_CHECK` -> `FOOT_FLAT_CHECK` -> `LEG_EXTENDED_CHECK` -> `HANDS_POSITION_CHECK` -> `FORWARD_REACH` -> `MEASUREMENT`
  - Countdown working: 3-2-1-GO audio and visual overlay confirmed

- **Video Countdown Integration:** Implemented countdown display system for the camera feed.
  - Added `countdown_phase`, `countdown_start_time`, `countdown_step` variables to `main()`
  - Green text overlay synchronized with MP3 audio playback

### Fixed

- **Tkinter Kernel Crash:** Replaced `get_user_info()` Tkinter dialog with `input()` prompts.
  - **Root cause:** NSApplication selector crash when called from Jupyter background thread on macOS
  - **Fix:** Replaced GUI dialog with terminal `input()` prompts in `main()`

- **Audio Path:** Fixed hardcoded absolute path in Cell 4.
  - **Before:** `sys.path.append('/Users/hinalsachpara/Desktop/...')`
  - **After:** `sys.path.append('.')` - works on any machine

- **Import Error (`cv2` not defined):** Documented correct cell execution order.
  - **Root cause:** Cell 1 (imports) was skipped before Cell 21 (main)
  - **Fix:** Run cells in order: 0, 1, 2, 4, 9–16, 18, 23, 21

### What I Learned

- Developed deeper understanding of macOS-specific threading constraints and their implications for Jupyter-based GUI interactions.
- Learned systematic debugging of Jupyter cell execution dependencies.

### Challenges

- Mac-specific OpenCV and Tkinter behaviours required platform-aware solutions that differed substantially from the Windows-oriented original implementation.

### To Do (Next Steps)

- [ ] Expand audio coverage to all 9 test states
- [ ] Create remaining instruction audio files and update TTS state mapping

---

## [March 2–6, 2026] - Week 7

### Summary
The development this week yielded two significant user experience enhancements: a two-screen pre-test instruction flow and a comprehensive error detection system. These features directly address usability and test validity requirements identified in earlier project phases.

### Added

- **Two-Screen Instruction Flow** - `show_instruction_screen()`
  - **Screen 1:** Six-step text instructions on white background - stays for 15 seconds or until keypress
  - **Screen 2:** Visual image guide (`merged_instruction.png`) - stays for 5 seconds or until keypress
  - Camera does not open until instruction flow fully completes
  - Image path uses `os.getcwd()` with hardcoded fallback - works on any machine

- **Error Detection System** - `show_error_message()`
  - Full-width red banner at top of camera feed, with state-specific messages:
    - No body detected: `"No body detected! Please step into the camera frame."`
    - `FULL_BODY_DETECTION`: `"Adjust camera! Make sure your full body is visible."`
    - `SITTING_CHECK`: `"Wrong position! Please sit on the edge of the chair."`
    - `FOOT_FLAT_CHECK`: `"Place one foot flat on the floor!"`
    - `LEG_EXTENDED_CHECK`: `"Extend your leg straight forward!"`
    - `HANDS_POSITION_CHECK`: `"Place one hand on top of the other!"`
    - `FORWARD_REACH`: `"Exhale and reach forward toward your toes!"`

- **30-Second Test Timer:**
  - Displays `Time: Xs` at bottom center, counting down from 30
  - Green for 30–10 seconds, switches to red for final 10 seconds
  - Rendered inside a black background bar for readability on any camera background

- **Non-Overlapping Screen Layout:**

  | Zone | Position |
  |---|---|
  | Error / warning message | Top - full-width red bar |
  | Instruction text | Below error - black background bar |
  | Status message | Below instruction - centered |
  | Camera feed | Middle of screen |
  | 30-second timer | Bottom - black background bar |

### Fixed

- **macOS `cv2.waitKey()` Non-Response:**
  - **Root cause:** OpenCV windows do not receive keyboard focus before timeout fires on macOS
  - **Fix:** Replaced `cv2.waitKey(5000)` with `while time.time() - start < 15.0: cv2.waitKey(1)` loop

- **Audio/Countdown Desync:**
  - **Root cause:** Camera and countdown loop were running in the background during instruction screens
  - **Fix:** Moved `cv2.VideoCapture(0)` to after `show_instruction_screen()` returns; added `time.sleep(0.5)` buffer before audio plays

### What I Learned

- Learned to design instruction flows that accommodate platform-specific windowing constraints - particularly macOS's refusal to grant keyboard focus to OpenCV windows in fullscreen mode.
- Understood the UX importance of non-overlapping information zones for readability under real-world camera conditions.

### Challenges

- Multiple layout conflicts (overlapping text zones, instruction cutoff, missing steps) required iterative redesign before a stable layout was achieved.

### To Do (Next Steps)

- [ ] Replace `merged_instruction.png` with a cleaner visual guide
- [ ] Wire remaining audio instructions to all test states
- [ ] Record demo video after completing timer measurement logic

---

## [March 9–13, 2026] - Week 8

### Summary
This week involved significant refactoring of key validation functions and the implementation of additional test flow states. The changes directly improved measurement accuracy and reduced the frequency of false-negative validation failures observed during testing.

### Added

- **`HOLD_POSITION` State Wired in `main()`:** Was defined in the state machine but never validated.
  - Reuses `check_forward_reach()` - shows "Hold still! Measuring..."
  - 2-second hold required before advancing to `MEASUREMENT`

- **`INHALE_PREPARATION` State Restored:** Was missing from the validation block in `main()`.
  - Added back using existing `check_inhale()` function

- **Pre-Countdown Full Body Detection Phase:**
  - Camera opens immediately after instruction screens
  - Shows "Position yourself fully in the camera frame" until full body detected
  - Green "Perfect! Get ready..." confirmation for 2 seconds, then countdown fires
  - `FULL_BODY_DETECTION` removed from test loop - handled in pre-countdown phase instead

### Changed

- **`check_hands_position()` Completely Rewritten:**
  - **Root cause of failure:** Old 3D distance threshold `0.1` was physically unachievable - observed values ranged `0.50–0.72`
  - **New logic (Rikli & Jones protocol):** Wrist Y-difference `< 0.08`, wrist X-difference `< 0.25`, wrists below shoulders
  - **Impact:** 3 specific feedback messages; function now passes reliably

- **`check_forward_reach()` Fixed:**
  - **Root cause of failure:** `below_knee` check always returned `False` due to side-view camera angle - confirmed across 50-frame debug log
  - **Fix:** Removed unreliable check; now validates horizontal alignment only (`x_diff < 0.2` relative to extended ankle)

- **Countdown Audio/Visual Sync Fixed:**
  - `play_audio()` now fires once when each step starts; text drawn once per frame
  - Eliminated double-draw bug causing overlapping/garbled countdown text

### What I Learned

- Developed confidence in empirical threshold calibration - the importance of instrumenting code with debug output before assuming threshold values are valid.
- Learned to design pose validation logic that accounts for camera angle constraints, a non-trivial consideration in monocular vision systems.

### Challenges

- Diagnosing why `check_hands_position()` never passed required adding extensive debug instrumentation, which revealed that the original threshold had no grounding in observed MediaPipe landmark coordinates.

### To Do (Next Steps)

- [ ] Implement fullscreen display mode
- [ ] Clarify timer measurement logic with supervisor
- [ ] Record demo video

---

## [March 16–20, 2026] - Week 9

### Summary
This week produced the result screen and timer pause/resume system - two features that complete the core user-facing functionality of the test. The work also included a significant UX decision: raw measurement values were removed from the user-facing display in favour of clinically meaningful categorical feedback.

### Added

- **End Screen / Result Screen** - `show_result_screen()`
  - **Trigger 1:** Fires when `TestState.COMPLETE` is reached
  - **Trigger 2:** Fires when 30-second timer hits 0 (safety net)
  - **Background:** Freezes last live camera frame, applies Gaussian blur `(55, 55)` with 65% dark overlay
  - **Layout:** Navy blue header banner, "TEST COMPLETE" label, semi-transparent result card, bottom exit bar
  - **Result card:** Category label in cyan, motivational message in green
  - **Animation:** 3-pulse green border on entry; waits for any keypress to exit
  - `result_screen_shown` flag prevents double trigger; `r` key resets flag for a fresh run

- **Timer Pause/Resume Logic:**
  - Timer pauses immediately when user breaks position during test
  - Timer resumes automatically when user corrects position
  - **3-chance rule:** on 3rd position break, test fails and restarts from pre-countdown screen
  - `"PAUSED | Time: Xs"` displayed in orange when paused
  - `"Position broken! Attempt X of 2 - correct position to resume"` shown in dark blue banner

- **Camera Out-of-Frame Detection:**
  - Full body visibility check during test phase using existing `check_full_body()`
  - Differentiates camera visibility issue from positional error - avoids misleading user feedback
  - Both conditions trigger timer pause and count as a position break

- **`reset_to_pre_countdown()` Function:** Clean, reusable reset covering all test state variables.

- **Fullscreen Display:** Test window now opens in fullscreen automatically via `cv2.setWindowProperty`.

### Changed

- **`measure_flexibility()` - Updated Category Logic:**
  - New 3-category system based on Rikli & Jones protocol:
    - **Above Average:** fingertips past toes by more than 4 inches
    - **Average:** fingertips within 4 inches either side of toes
    - **Below Average:** fingertips more than 4 inches short of toes
  - Raw inches now printed to terminal only: `[DEBUG] Right leg: 3.9 inches | Category: Average`
  - Result screen shows plain-English category and motivational message only

- **Result Message Wording Clarified:**
  - **Before:** `"Right leg: 3.9 in past toes."` - ambiguous
  - **After:** `"Right leg: fingertips reached 3.9 inches beyond toes."` - clear and descriptive

### Fixed

- **Fullscreen Instruction Screen Hanging:**
  - **Root cause:** `cv2.waitKey()` stops responding in Mac fullscreen mode - macOS withholds keyboard focus from OpenCV windows
  - **Fix:** Removed all keypress detection from instruction screens; both screens now exit purely on time
  - Bottom bar text updated from `"Press any key..."` to `"Starting in 5 seconds..."`

### What I Learned

- Understood the clinical rationale for categorical rather than raw numerical result display - reducing cognitive burden on elderly users and avoiding misinterpretation of precise decimal values.
- Gained experience designing stateful UI logic (pause/resume/restart) within a single-threaded OpenCV event loop.

### Challenges

- Implementing fullscreen mode exposed additional macOS-specific issues with `cv2.waitKey()` unresponsiveness, requiring a shift from keypress-based to time-based screen transitions throughout.

### To Do (Next Steps)

- [ ] Run 12 structured edge case tests and document pass/fail outcomes
- [ ] Record Video 1 - clean full successful test run
- [ ] Record Video 2 - interrupted test with pause/resume/restart
- [ ] Push final version to GitHub

---

## [March 23–27, 2026] - Week 10

### Summary
Focus this week shifted to instruction refinement and system validation planning. Following feedback from the supervisor on instruction content, significant effort was invested in balancing instructional completeness with UX readability constraints.

### Work Done

- **Instruction Screen Document Created and Shared:** Covered pre-test setup guidance, user positioning steps, and test procedure.
  - Received feedback to shorten and simplify content to align with UX readability standards

- **UI Style Guide Reviewed:** Examined fonts, colour palette, and button styles; mapped applicable constraints to the OpenCV-based interface.

- **Team Alignment Meeting:** Attended team meeting and aligned on validation strategy and edge case testing scope.
  - Documented meeting notes and action items for distribution

### What I Learned

- Reinforced understanding of the tension between informational completeness and cognitive load in instruction design - particularly for health applications targeting older adult users.
- Learned how UI style guide constraints influence content decisions, not just visual presentation.

### Challenges

- Condensing six-step instructions into a display-appropriate format without losing critical safety or positioning information required multiple revision cycles.

### To Do (Next Steps)

- [ ] Refine and shorten instruction content based on feedback
- [ ] Align implementation with shared UI style guide
- [ ] Prepare for final integration of instruction screens

---

## [March 30 – April 3, 2026] - Week 11

### Summary
The week focused on finalising test instructions, aligning cross-module camera setup guidance with the teammate, and initiating structured edge case testing. The commencement of real-world validation testing represents a transition into the final phase of the work term.

### Work Done

- **Final Test Instructions Produced:** Covered proper sitting posture, feet placement, arm position, movement rules, and timer-based completion logic.
  - Submitted for supervisor review and approval

- **Cross-Module Camera Instructions Standardized:** Collaborated with teammate to align camera setup guidance across both test modules, ensuring a consistent user experience at the application level.

- **Edge Case Testing Initiated:**
  - Participated in team discussion; documented scope covering lighting, visibility, and movement variability scenarios
  - Commenced testing with dark room / low-lighting conditions

### What I Learned

- Understood the importance of cross-module instruction consistency when multiple team members contribute independently developed components to a unified application.
- Gained practical exposure to the structured approach required for systematic edge case validation in computer vision systems.

### Challenges

- Handling environment-dependent variability (camera angle, lighting, background clutter) introduced test conditions that are difficult to reproduce deterministically.

### To Do (Next Steps)

- [ ] Continue and complete edge case testing across all defined scenarios
- [ ] Document results in a structured test report
- [ ] Record and share demo videos (successful and interrupted run cases)

---

## [April 6–10, 2026] - Week 12

### Summary
This week delivered the instruction screen implementation with multimedia support and added real-time edge case handling. A significant architectural limitation was also identified and documented: OpenCV's constraints as a UI framework for delivering polished, style-guided instruction interfaces.

### Added

- **Instruction Screens with Multimedia Support:**
  - Basic and test instruction screens with visual guidance images and audio narration
  - Edge case handling integrated into the live camera feed:
    - Poor lighting detected -> on-screen warning message (test continues)
    - Multiple people in frame -> warning message displayed (test continues)

### Changed

- **Architecture Recommendation - Instruction Screen Migration:**
  - **Limitation identified:** OpenCV does not support custom fonts or CSS-based styling, preventing design system compliance
  - **Proposed solution:** Migrate instruction screens to an HTML/CSS-based interface executed prior to OpenCV camera initialisation
  - **Impact:** Enables full design system compliance while keeping the computer vision pipeline unchanged

### What I Learned

- Developed a clearer understanding of the boundary between computer vision frameworks and frontend UI toolkits - and the trade-offs involved in using OpenCV for presentation-layer concerns.
- Gained experience in identifying architectural constraints early and proposing pragmatic, incremental migration strategies.

### Challenges

- Implementing design-system compliance within OpenCV's rendering constraints proved intractable for the current iteration, necessitating a longer-term architectural recommendation.

### To Do (Next Steps)

- [ ] Evaluate feasibility of HTML/CSS instruction screen integration
- [ ] Continue refining edge case handling based on test results
- [ ] Improve UI consistency with the design system where OpenCV permits

---

## [April 13–17, 2026] - Week 13

### Summary
The final week of the work term was dedicated to comprehensive edge case testing and the production of a structured validation report. Collaborative documentation with the teammate ensured the report reflects the full scope of real-world test scenarios evaluated across both modules.

### Work Done

- **Systematic Edge Case Testing Conducted** across three categories:
  - **Lighting variations:** dark room, direct sunlight, fluorescent glare
  - **Camera visibility and positioning:** partial occlusion, distance, angle variations
  - **Movement and interruption scenarios:** mid-test pause, multiple people, rapid movement

- **Structured Test Report Produced:** Documented all results using the established template.
  - Fields: scenario, steps taken, expected behaviour, actual behaviour, fixable via code

- **Combined Testing Document Finalized:** Collaborated with teammate to compile and finalize the report across both modules.
  - Submitted to supervisor for review and feedback

### What I Learned

- Developed practical competency in systematic software validation, particularly for computer vision systems that are sensitive to uncontrolled environmental variables.
- Understood that rigorous documentation of both pass and fail cases is equally important in producing a trustworthy validation record.
- Gained experience in collaborative documentation - ensuring that independently conducted tests produce a coherent, consistently formatted report.

### Challenges

- Ensuring comprehensive coverage of all real-world scenarios within the available timeframe required prioritizing the highest-risk edge cases.
- Validating consistent system behaviour across heterogeneous environments (different rooms, cameras, lighting rigs) introduced non-determinism that was difficult to fully control.

### To Do (Next Steps)

- [ ] Incorporate supervisor feedback on testing results
- [ ] Address any critical edge cases identified during the review
- [ ] Finalize the system for stable handoff and deployment readiness

---
