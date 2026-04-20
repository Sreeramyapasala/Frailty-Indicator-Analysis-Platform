Week 1 — January 20–23, 2026
Summary
The first week was dedicated to project onboarding and establishing a foundational understanding of the Sit-to-Stand Frailty Assessment System. Rather than beginning implementation prematurely, the focus was placed on comprehending the system architecture, stakeholder expectations, and the broader clinical context underpinning the project.
Work Done

Received and reviewed project onboarding materials and task specifications from the Product Manager.
Attended a project kickoff meeting on January 22 to clarify workflow expectations and deliverable timelines.
Conducted a thorough review of the project repository, examining the existing Sit-to-Stand test implementation.
Identified the system's core mechanism: webcam-based computer vision for automated repetition counting and test execution.
Reviewed assigned research tasks: CDC STEADI chair stand test protocols, age-group score interpretation, and current system limitations.

What I Learned

Acquired foundational knowledge of frailty assessment methodologies and the clinical significance of the Sit-to-Stand test in geriatric health screening.
Understood how computer vision techniques are applied to automate physical performance test scoring.
Recognized the critical role of interpretable, user-facing result outputs in health-oriented software systems.

Challenges

Navigating an unfamiliar codebase while simultaneously learning domain-specific health concepts required careful time management and structured note-taking.
Bridging the gap between clinical standards (CDC STEADI) and their practical representation in software logic presented an initial conceptual challenge.

Future Scope / Next Steps

Initiate in-depth research on CDC STEADI scoring guidelines and age-stratified result interpretation.
Draft a preliminary design for the result interpretation and messaging component.
Investigate data storage options for retaining test results across sessions.

Non-Technical Contributions

Established communication channels with the Project Manager and clarified role expectations.
Developed an understanding of the team's Agile-style workflow and GitHub-based collaboration process.


Week 2 — January 26–30, 2026
Summary
This week focused on structured research into the CDC STEADI 30-Second Chair Stand Test, culminating in a documentation artefact that translated clinical scoring standards into actionable system-level requirements. Deliverables were shared with the Project Manager via GitHub and reviewed in a mid-week meeting.
Work Done

Conducted a comprehensive review of CDC STEADI guidelines for the 30-second chair stand test, including age- and gender-stratified normative score ranges.
Identified a critical system limitation: a single test metric is insufficient for robust fall-risk assessment and must be contextualized with additional health indicators.
Produced a structured documentation artefact comprising: age-based scoring benchmarks, caution conditions for edge-case result interpretation, and recommended supplementary data points.
Proposed a plain-text result summary generation feature to translate raw scores into user-comprehensible output.
Uploaded deliverables to GitHub and communicated progress to the Project Manager in advance of the January 28 meeting.

What I Learned

Gained a nuanced understanding of age-specific scoring in health data interpretation and the limitations of single-metric assessment tools.
Developed skills in translating technical output into clinically appropriate, user-friendly summaries aligned with health informatics best practices.

Challenges

Interpreting CDC medical guidelines in sufficient depth to derive meaningful software requirements demanded careful cross-referencing of clinical literature.
Ensuring that proposed system improvements remained practically implementable rather than purely theoretical required continuous alignment with the existing architecture.

Future Scope / Next Steps

Begin integrating result summary generation logic into the system output pipeline.
Explore storing contextual patient data (fall history, balance scores) alongside test results.
Improve usability and reliability of the result display module.

Non-Technical Contributions

Conducted and prepared for a structured meeting with the Project Manager (January 28), demonstrating the ability to communicate research findings clearly.
Strengthened documentation and technical communication skills through GitHub-based collaboration.


Week 3 — February 2–8, 2026
Summary
Week three marked a transition from independent research into collaborative development. Engagement with the teammate who built the base Sit-to-Stand system provided critical architectural insight and enabled a more targeted approach to the result messaging contribution.
Work Done

Attended a technical discussion session with the teammate on February 4 to understand the existing implementation, state machine logic, and identified improvement areas.
Mapped the result messaging feature onto specific system components to determine integration points.
Revisited prior research and aligned findings with actual system behavior and constraints.
Planned the architecture for integrating plain-language result summaries into the test completion workflow.

What I Learned

Developed proficiency in reading and reasoning about unfamiliar codebases, particularly event-driven systems with multi-stage validation logic.
Understood the interdependencies between UI rendering, state management, and output logic in the existing system.
Recognized the importance of collaborative knowledge transfer when modifying established software systems.

Challenges

Navigating another developer's architectural decisions required significant reverse-engineering effort before implementation planning could begin.
Mapping abstract research recommendations onto concrete, integration-ready features presented non-trivial design challenges.

Future Scope / Next Steps

Implement result summary generation logic within the identified system components.
Ensure cross-platform compatibility of the output module.
Validate messaging logic across diverse age and score scenarios.

Non-Technical Contributions

Established effective collaboration norms with the teammate, including a clear division of responsibilities: teammate leading UX, self leading messaging and output logic.


Week 4 — February 9–13, 2026
Summary
This week involved consolidating role clarity and preparing for implementation. While active development was minimal, the week served an important organizational function — ensuring that contribution boundaries were well-defined and implementation plans were aligned with project expectations.
Work Done

Reviewed and confirmed role assignment documentation, formally taking ownership of the result messaging and interpretation component.
Defined expected behaviour and edge cases for user-facing output messages across different test outcomes.
Prepared an implementation plan for the messaging module to ensure alignment with the broader system architecture.

What I Learned

Appreciated the importance of explicit role delineation in team-based software projects to minimize duplication and integration conflicts.
Understood how separating UX concerns from business logic leads to more maintainable and testable system design.

Challenges

Balancing the need for thorough planning against the risk of over-engineering a relatively bounded feature required careful scope management.

Future Scope / Next Steps

Begin implementation of the result messaging module.
Validate messaging outputs with the teammate to ensure consistency with the UX layer.

Non-Technical Contributions

Demonstrated professional accountability by formally committing to a project component and communicating ownership to the team.


Week 5 — February 16–20, 2026
Summary
Development accelerated this week with the implementation of a cross-platform text-to-speech (TTS) system, addressing a critical dependency issue with the prior Windows-only audio architecture. This work directly expanded the deployment viability of the application.
Work Done

Evaluated TTS alternatives (pyttsx3, gTTS, Web Speech API) and selected a pure MP3 playback approach for maximum cross-platform reliability.
Developed and tested tts_final.py, a complete TTS implementation using pre-generated MP3 audio files (TTSMaker neural voice, American female, consistent tone).
Produced all required audio assets: countdown files (3.mp3, 2.mp3, 1.mp3, go.mp3) and instructional voice-overs (instruction_sit.mp3, instruction_extend.mp3, instruction_hold.mp3, instruction_relax.mp3).
Confirmed total audio asset footprint at 92 KB — well within the 100 KB project constraint.
Replaced the Windows-only win32com.client SpeechManager with the FullMP3TTS class, enabling Mac/Windows/Linux compatibility from a unified codebase.

What I Learned

Gained practical experience evaluating and selecting TTS libraries against cross-platform, quality, and cost constraints.
Learned that dependency isolation (pre-generated MP3s vs. runtime synthesis) can significantly improve deployment portability.

Challenges

Ensuring audio/visual synchronization between MP3 playback and the OpenCV video countdown required careful timing logic to prevent desynchronization.

Future Scope / Next Steps

Integrate the TTS system fully into the main Jupyter notebook.
Synchronize audio playback with visual countdown overlays in the camera feed.

Non-Technical Contributions

Demonstrated initiative in identifying and eliminating a platform-specific dependency without disrupting existing functionality.


Week 6 — February 23–27, 2026
Summary
This week was focused on the full integration of the TTS system into the primary notebook and implementing the video countdown overlay. A number of cross-platform compatibility issues were resolved, advancing the system toward a stable, end-to-end functional state.
Work Done

Integrated tts_final.py into chair_sit_and_reach_final_working_Hinal.ipynb, replacing all Windows-specific audio calls.
Implemented the visual countdown overlay system, including countdown_phase, countdown_start_time, and countdown_step variables with green text rendering synchronized to MP3 playback.
Addressed and resolved path dependency issues — replaced hardcoded absolute paths with sys.path.append('.') for universal portability.
Resolved a Tkinter kernel crash on macOS by replacing the GUI-based get_user_info() dialog with terminal input() prompts.
Documented correct Jupyter cell execution order to prevent cv2 not defined import errors.
Conducted a full end-to-end test, confirming all 7 pipeline stages executed correctly and audio/visual countdown functioned as expected.

What I Learned

Developed deeper understanding of macOS-specific threading constraints (NSApplication selector crash) and their implications for Jupyter-based GUI interactions.
Learned systematic debugging of Jupyter cell execution dependencies.

Challenges

Mac-specific OpenCV and Tkinter behaviours required platform-aware solutions that differed substantially from the Windows-oriented original implementation.

Future Scope / Next Steps

Expand audio coverage to all 9 test states.
Create remaining instruction audio files and update TTS mapping.

Non-Technical Contributions

Committed fixes to GitHub with clear commit messages, maintaining clean version history for the team.


Week 7 — March 2–6, 2026
Summary
The development this week yielded two significant user experience enhancements: a two-screen pre-test instruction flow and a comprehensive error detection system. These features directly address usability and test validity requirements identified in earlier project phases.
Work Done

Implemented show_instruction_screen() — a two-screen instruction sequence: Screen 1 presents six-step text instructions for 15 seconds; Screen 2 displays a visual image guide (merged_instruction.png) for 5 seconds. Camera activation is deferred until instruction flow completes.
Built show_error_message() — a real-time error display system that renders context-specific guidance as a full-width red banner at the top of the camera feed for each of the 7 test states.
Implemented a 30-second test timer with dynamic colour feedback: green for 30–10 seconds, red for the final 10 seconds, rendered in a dedicated bottom-bar zone.
Redesigned the screen layout into non-overlapping zones: error banner (top), instruction text, status message, camera feed, and timer (bottom).
Resolved macOS-specific OpenCV focus issues — replaced cv2.waitKey(N) timeouts with time-loop patterns compatible with Mac fullscreen behaviour.

What I Learned

Learned to design instruction flows that accommodate platform-specific windowing constraints — particularly macOS's refusal to grant keyboard focus to OpenCV windows in fullscreen mode.
Understood the UX importance of non-overlapping information zones for readability under real-world camera conditions.

Challenges

Multiple layout conflicts (overlapping text zones, instruction cutoff, missing steps) required iterative redesign before a stable layout was achieved.

Future Scope / Next Steps

Replace merged_instruction.png with a cleaner visual guide.
Wire remaining audio instructions to all test states.
Record demo video after completing timer measurement logic.

Non-Technical Contributions

Maintained a detailed problem/fix log throughout development, demonstrating systematic debugging practice.


Week 8 — March 9–13, 2026
Summary
This week involved significant refactoring of key validation functions and the implementation of additional test flow states. The changes directly improved measurement accuracy and reduced the frequency of false-negative validation failures observed during testing.
Work Done

Completely rewrote check_hands_position() — the previous 3D distance threshold (0.1) was empirically unachievable (observed values: 0.50–0.72). The rewritten function implements Rikli & Jones protocol: wrist Y-difference < 0.08, wrist X-difference < 0.25, wrists below shoulders — with three distinct user-facing feedback messages.
Fixed check_forward_reach() — removed the below_knee check, which was structurally unreliable from side-view camera angles (confirmed via 50-frame debug log consistently returning False). Replaced with horizontal alignment check (x_diff < 0.2 relative to extended ankle).
Wired the HOLD_POSITION state in main() — previously defined in the state machine but never validated. Implemented a 2-second hold requirement before advancing to MEASUREMENT.
Re-integrated INHALE_PREPARATION state using the existing check_inhale() function.
Implemented the pre-countdown full body detection phase: camera activates and waits for full body in frame before initiating countdown.
Fixed countdown audio/visual desynchronization — audio now fires after the frame is drawn and displayed, eliminating the case where audio preceded the visual number.

What I Learned

Developed confidence in empirical threshold calibration — the importance of instrumenting code with debug output before assuming threshold values are valid.
Learned to design pose validation logic that accounts for camera angle constraints, a non-trivial consideration in monocular vision systems.

Challenges

Diagnosing why check_hands_position() never passed required adding extensive debug instrumentation, which revealed that the original threshold had no grounding in observed MediaPipe landmark coordinates.

Future Scope / Next Steps

Implement fullscreen display mode.
Clarify timer measurement logic with supervisor.
Record demo video.

Non-Technical Contributions

Demonstrated strong analytical debugging skills, moving systematically from symptom to root cause rather than making speculative code changes.


Week 9 — March 16–20, 2026
Summary
This week produced the result screen and timer pause/resume system — two features that complete the core user-facing functionality of the test. The work also included a significant UX decision: raw measurement values were removed from the user-facing display in favour of clinically meaningful categorical feedback.
Work Done

Implemented show_result_screen() — triggered on TestState.COMPLETE or 30-second timer expiry. Features: frozen blurred camera frame background, navy header, semi-transparent result card, 3-pulse border animation, and keypress-to-exit.
Updated measure_flexibility() to implement a three-category Rikli & Jones classification: Above Average (>4 inches past toes), Average (within ±4 inches), Below Average (>4 inches short). Raw measurements are now printed to terminal only as debug output.
Implemented timer pause/resume logic with a three-chance rule: timer pauses on position break, resumes on correction; third break triggers a full test restart. Visual indicators (orange PAUSED bar, dark blue attempt counter) provide real-time feedback.
Implemented camera out-of-frame detection — differentiates between camera visibility issues and positional errors, preventing misleading error messages.
Created reset_to_pre_countdown() — a reusable reset function covering all test state variables.
Enabled fullscreen display via cv2.setWindowProperty with WINDOW_FULLSCREEN.

What I Learned

Understood the clinical rationale for categorical rather than raw numerical result display — reducing cognitive burden on elderly users and avoiding misinterpretation of precise decimal values.
Gained experience designing stateful UI logic (pause/resume/restart) within a single-threaded OpenCV event loop.

Challenges

Implementing fullscreen mode exposed additional macOS-specific issues with cv2.waitKey() unresponsiveness. Resolved by removing all keypress-dependent exits from instruction screens and using time-based transitions exclusively.

Future Scope / Next Steps

Run 12 structured edge case tests and document pass/fail outcomes.
Record demo video — clean run and interrupted run with pause/resume.
Send update to supervisor with results and videos.
Push final version to GitHub.

Non-Technical Contributions

Communicated a structured update to the supervisor, demonstrating professional progress reporting.


Week 10 — March 23–27, 2026
Summary
Focus this week shifted to instruction refinement and system validation planning. Following feedback from the Project Manager on the instruction content, significant effort was invested in balancing instructional completeness with UX readability constraints.
Work Done

Created and shared a comprehensive instruction screen document covering pre-test setup guidance, user positioning steps, and test procedure.
Received and incorporated feedback from the Project Manager: shortened and simplified instruction content to align with UX standards for readability.
Reviewed the project UI style guide (fonts, colour palette, button styles) and mapped applicable constraints to the OpenCV-based interface.
Attended team meeting and aligned on the next phase: validation strategy and edge case testing scope.
Documented meeting notes and action items for distribution to the team.

What I Learned

Reinforced understanding of the tension between informational completeness and cognitive load in instruction design — particularly for health applications targeting older adult users.
Learned how UI style guide constraints influence content decisions, not just visual ones.

Challenges

Condensing six-step instructions into a display-appropriate format without losing critical safety or positioning information required multiple revision cycles.

Future Scope / Next Steps

Refine instruction content based on PM feedback.
Align implementation with shared UI style guide.
Prepare for final integration of instruction screens into the system.

Non-Technical Contributions

Demonstrated responsiveness to feedback by revising deliverables promptly and communicating changes clearly.


Week 11 — March 30 – April 3, 2026
Summary
The week focused on finalising test instructions, aligning cross-module camera setup guidance with the teammate, and initiating structured edge case testing. The commencement of real-world validation testing represents a transition into the final phase of the work term.
Work Done

Produced and shared final test instructions for the Sit-to-Stand test covering posture, foot placement, arm positioning, movement rules, and timer-based completion logic.
Collaborated with teammate to standardize camera setup instructions across both test modules, ensuring a consistent user experience at the application level.
Submitted instructions for PM review and approval.
Participated in a team discussion on edge case testing strategy; documented scope to include lighting, visibility, and movement variability scenarios.
Initiated edge case testing — commenced with dark room / low-lighting conditions.

What I Learned

Understood the importance of cross-module instruction consistency when multiple team members contribute independently developed components to a unified application.
Gained practical exposure to the structured approach required for systematic edge case validation in computer vision systems.

Challenges

Handling environment-dependent variability (camera angle, lighting, background clutter) introduced test conditions that are difficult to reproduce deterministically.

Future Scope / Next Steps

Continue and complete edge case testing across all defined scenarios.
Document results in a structured test report.
Record and share demo videos (successful and interrupted run cases).

Non-Technical Contributions

Maintained close coordination with teammate; communicated meeting outcomes clearly and promptly to the Project Manager.


Week 12 — April 6–10, 2026
Summary
This week delivered the instruction screen implementation with multimedia support and added real-time edge case handling. A significant architectural insight was also documented: the limitations of OpenCV as a UI framework for delivering polished, style-guided instruction interfaces.
Work Done

Implemented basic and test instruction screens with visual guidance images and audio narration support.
Added edge case detection and handling: low-lighting conditions trigger an on-screen warning; multiple persons in frame trigger a warning without interrupting the test.
Prepared and distributed a structured progress update to the PM prior to the scheduled meeting.
Identified and documented an architectural limitation: OpenCV does not support custom fonts or CSS-based styling, constraining the application's ability to implement the project's design system.
Proposed a practical solution: migrate instruction screens to an HTML/CSS-based interface executed prior to OpenCV camera initialisation.

What I Learned

Developed a clearer understanding of the boundary between computer vision frameworks and frontend UI toolkits — and the trade-offs involved in using OpenCV for presentation-layer concerns.
Gained experience in identifying architectural constraints early and proposing pragmatic, incremental migration strategies.

Challenges

Implementing design-system compliance within OpenCV's rendering constraints proved intractable for the current iteration, necessitating a longer-term architectural recommendation.

Future Scope / Next Steps

Evaluate feasibility of HTML/CSS instruction screen integration.
Continue refining edge case handling based on test results.
Improve UI consistency with the design system where OpenCV permits.

Non-Technical Contributions

Demonstrated proactive communication by sharing a written update before the meeting, allowing the PM to review progress in advance.


Week 13 — April 13–17, 2026
Summary
The final week of the work term was dedicated to comprehensive edge case testing and the production of a structured validation report. Collaborative documentation with the teammate ensured that the report reflects the full scope of real-world test scenarios evaluated across both modules.
Work Done

Conducted systematic edge case testing across three categories: lighting variations (dark room, direct sunlight, fluorescent glare), camera visibility and positioning (partial occlusion, distance, angle), and movement/interruption scenarios (mid-test pause, multiple people, rapid movement).
Documented all test results in a structured edge case testing report following the established template (scenario, steps taken, expected behaviour, actual behaviour, fixable via code).
Collaborated with teammate to compile and finalize the combined testing document.
Submitted the completed testing report to the PM for review and feedback.

What I Learned

Developed practical competency in systematic software validation, particularly for computer vision systems that are sensitive to uncontrolled environmental variables.
Understood that rigorous documentation of both pass and fail cases is equally important in producing a trustworthy validation record.
Gained experience in collaborative documentation — ensuring that independently conducted tests produce a coherent, consistently formatted report.

Challenges

Ensuring comprehensive coverage of all real-world scenarios within the available timeframe required prioritizing the highest-risk edge cases.
Validating consistent system behaviour across heterogeneous environments (different rooms, cameras, lighting rigs) introduced non-determinism that was difficult to fully control.

Future Scope / Next Steps

Incorporate PM feedback on testing results.
Address any critical edge cases identified during the review.
Finalize the system for stable handoff and deployment readiness.

Non-Technical Contributions

Demonstrated strong collaborative and documentation skills throughout the final validation phase, contributing to a complete and professionally presented project deliverable.