import cv2
import time
import numpy as np
import mediapipe as mp
import pygame
import os
import sys
import math


# ─────────────────────────────────────────────────────────────────
# AUDIO SETUP
# ─────────────────────────────────────────────────────────────────
sys.path.append('.')
pygame.mixer.init()

AUDIO_FILES = {
    'countdown_3':      'audio/3.mp3',
    'countdown_2':      'audio/2.mp3',
    'countdown_1':      'audio/1.mp3',
    'countdown_go':     'audio/go.mp3',
    'instruction_sit':  'audio/instruction_sit.mp3',
    'instruction_hold': 'audio/instruction_hold.mp3',
}

def play_audio(audio_key):
    """Play an MP3 file by key. Silently skips if file not found."""
    try:
        path = AUDIO_FILES.get(audio_key, '')
        if path and os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
        else:
            print(f"[Audio] File not found for key: {audio_key}")
    except Exception as e:
        print(f"[Audio] Playback error: {e}")


# ─────────────────────────────────────────────────────────────────
# INSTRUCTION SCREEN
# ─────────────────────────────────────────────────────────────────
def show_instruction_screen():
    """Show two-screen instruction display before the test starts."""

    # Screen 1: Text Instructions
    text_screen = np.ones((720, 1280, 3), dtype=np.uint8) * 255
    cv2.putText(text_screen, "30-Second Chair Stand Test - Instructions",
                (50, 70), cv2.FONT_HERSHEY_DUPLEX, 1.2, (30, 60, 150), 2)
    cv2.line(text_screen, (50, 110), (1230, 110), (30, 60, 150), 2)

    instructions = [
        "1. Sit in the MIDDLE of the chair, back straight",
        "2. Cross BOTH arms on your chest",
        "3. Make sure your KNEES are visible to the camera",
        "4. On GO - stand up FULLY, then sit back down",
        "5. Repeat as many times as possible in 30 seconds",
        "6. Do NOT use your arms to push yourself up",
    ]
    y = 180
    for line in instructions:
        cv2.putText(text_screen, line,
                    (50, y), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (50, 50, 50), 2)
        y += 80

    cv2.rectangle(text_screen, (0, 640), (1280, 720), (30, 60, 150), -1)
    cv2.putText(text_screen,
                "Study the steps carefully - press any key or wait 15 seconds...",
                (150, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow('Instructions', text_screen)
    start = time.time()
    while time.time() - start < 15.0:
        if cv2.waitKey(1) != -1:
            break

    # Screen 2: Image guide
    image_path = os.path.join(os.getcwd(), "merged_instruction.png")
    instruction_img = cv2.imread(image_path)
    if instruction_img is not None:
        instruction_img = cv2.resize(instruction_img, (1280, 720))
        cv2.rectangle(instruction_img, (0, 640), (1280, 720), (0, 0, 0), -1)
        cv2.putText(instruction_img,
                    "Press any key to start or wait 5 seconds...",
                    (350, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.imshow('Instructions', instruction_img)
        start = time.time()
        while time.time() - start < 5.0:
            if cv2.waitKey(1) != -1:
                break
    else:
        print("[Info] merged_instruction.png not found — skipping image screen.")

    cv2.destroyAllWindows()
    time.sleep(0.5)
    print("Instructions done!")


# ─────────────────────────────────────────────────────────────────
# AUDIBLE COUNTDOWN
# ─────────────────────────────────────────────────────────────────
def play_audible_countdown(cap, window_name="30-Second Chair Stand Test"):
    """Show 3-2-1-GO on camera feed AND play audio for each number."""
    audio_keys = ['countdown_3', 'countdown_2', 'countdown_1', 'countdown_go']
    messages   = ["Get Ready: 3", "Get Ready: 2", "Get Ready: 1", "GO!"]

    for step in range(4):
        play_audio(audio_keys[step])
        deadline = time.time() + 1.5
        while time.time() < deadline:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            txt  = messages[step]
            size = cv2.getTextSize(txt, cv2.FONT_HERSHEY_DUPLEX, 3, 4)[0]
            tx   = (frame.shape[1] - size[0]) // 2
            ty   = (frame.shape[0] + size[1]) // 2
            cv2.putText(frame, txt, (tx, ty),
                        cv2.FONT_HERSHEY_DUPLEX, 3, (0, 255, 0), 6)
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)


# ─────────────────────────────────────────────────────────────────
# POSITION VERIFICATION FUNCTIONS (from friend's sit-and-reach code)
# Added here — not in your original
# ─────────────────────────────────────────────────────────────────
mp_pose_global = mp.solutions.pose

def check_full_body(landmarks):
    """Ensure the full person is detected before starting test."""
    key_points = [
        mp_pose_global.PoseLandmark.LEFT_SHOULDER,
        mp_pose_global.PoseLandmark.RIGHT_SHOULDER,
        mp_pose_global.PoseLandmark.LEFT_HIP,
        mp_pose_global.PoseLandmark.RIGHT_HIP,
        mp_pose_global.PoseLandmark.LEFT_KNEE,
        mp_pose_global.PoseLandmark.RIGHT_KNEE,
        mp_pose_global.PoseLandmark.LEFT_ANKLE,
        mp_pose_global.PoseLandmark.RIGHT_ANKLE,
        mp_pose_global.PoseLandmark.LEFT_FOOT_INDEX,
        mp_pose_global.PoseLandmark.RIGHT_FOOT_INDEX,
    ]
    VISIBLE_THRESHOLD = 0.4  # Lowered from 0.6 to be less strict on camera angle
    visible_count = sum(
        1 for kp in key_points
        if landmarks[kp.value].visibility > VISIBLE_THRESHOLD
    )
    if visible_count >= len(key_points) - 2:  # Allow up to 2 landmarks to be missed
        return True, "Full body detected"
    return False, "Step back so your full body is visible in camera"


def check_sitting_position(landmarks):
    """Check if person is sitting based on hip and knee Y positions."""
    left_hip   = landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value]
    right_hip  = landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value]
    left_knee  = landmarks[mp_pose_global.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose_global.PoseLandmark.RIGHT_KNEE.value]

    avg_hip_y  = (left_hip.y  + right_hip.y)  / 2
    avg_knee_y = (left_knee.y + right_knee.y) / 2
    hip_knee_distance = abs(avg_hip_y - avg_knee_y)

    if hip_knee_distance < 0.15:  # Increased from 0.09 — easier to detect sitting
        return True, "Sitting position detected"
    return False, "Not sitting - please sit on edge of chair"


def check_foot_flat_on_floor(landmarks):
    """Checks if at least one foot is flat on the floor."""
    Y_TOL = 0.06

    def foot_flat(heel, toe):
        return abs(heel.y - toe.y) < Y_TOL

    left_flat = foot_flat(
        landmarks[mp_pose_global.PoseLandmark.LEFT_HEEL.value],
        landmarks[mp_pose_global.PoseLandmark.LEFT_FOOT_INDEX.value]
    )
    right_flat = foot_flat(
        landmarks[mp_pose_global.PoseLandmark.RIGHT_HEEL.value],
        landmarks[mp_pose_global.PoseLandmark.RIGHT_FOOT_INDEX.value]
    )

    if left_flat or right_flat:
        return True, "Foot is flat on the floor"
    return False, "Please place one foot flat on the floor"


def calculate_angle_3d(a, b, c):
    """Calculates the angle at point b in 3D given points a, b, c."""
    ba = (a.x - b.x, a.y - b.y, a.z - b.z)
    bc = (c.x - b.x, c.y - b.y, c.z - b.z)
    dot_product = ba[0]*bc[0] + ba[1]*bc[1] + ba[2]*bc[2]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2 + ba[2]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2 + bc[2]**2)
    if mag_ba == 0 or mag_bc == 0:
        return 0
    angle_rad = math.acos(max(min(dot_product / (mag_ba * mag_bc), 1.0), -1.0))
    return math.degrees(angle_rad)


def check_leg_extended(landmarks):
    """Checks if either leg is straight using 3D hip-knee-ankle angle."""
    lh = landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value]
    lk = landmarks[mp_pose_global.PoseLandmark.LEFT_KNEE.value]
    la = landmarks[mp_pose_global.PoseLandmark.LEFT_ANKLE.value]
    rh = landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value]
    rk = landmarks[mp_pose_global.PoseLandmark.RIGHT_KNEE.value]
    ra = landmarks[mp_pose_global.PoseLandmark.RIGHT_ANKLE.value]

    left_knee_angle  = calculate_angle_3d(lh, lk, la)
    right_knee_angle = calculate_angle_3d(rh, rk, ra)

    # Also check ankle Y vs knee Y for front-facing cameras
    left_ankle_higher  = (lk.y - la.y) > 0.05
    right_ankle_higher = (rk.y - ra.y) > 0.05

    ANGLE_THRESHOLD = 130
    if (left_knee_angle > ANGLE_THRESHOLD or right_knee_angle > ANGLE_THRESHOLD
            or left_ankle_higher or right_ankle_higher):
        return True, "Leg is straight"
    return False, "Please extend one leg straight"


def hand_center(hand_landmarks):
    """Calculate 3D center of wrist, index, and pinky."""
    x = (hand_landmarks[0].x + hand_landmarks[1].x + hand_landmarks[2].x) / 3
    y = (hand_landmarks[0].y + hand_landmarks[1].y + hand_landmarks[2].y) / 3
    z = (hand_landmarks[0].z + hand_landmarks[1].z + hand_landmarks[2].z) / 3
    return type('Point', (object,), {'x': x, 'y': y, 'z': z})()


def check_hands_stacked(landmarks):
    """Checks if one hand is on top of the other."""
    left_landmarks = [
        landmarks[mp_pose_global.PoseLandmark.LEFT_WRIST.value],
        landmarks[mp_pose_global.PoseLandmark.LEFT_INDEX.value],
        landmarks[mp_pose_global.PoseLandmark.LEFT_PINKY.value]
    ]
    right_landmarks = [
        landmarks[mp_pose_global.PoseLandmark.RIGHT_WRIST.value],
        landmarks[mp_pose_global.PoseLandmark.RIGHT_INDEX.value],
        landmarks[mp_pose_global.PoseLandmark.RIGHT_PINKY.value]
    ]
    left_center  = hand_center(left_landmarks)
    right_center = hand_center(right_landmarks)

    dist = math.sqrt(
        (left_center.x - right_center.x)**2 +
        (left_center.y - right_center.y)**2 +
        (left_center.z - right_center.z)**2
    )
    if dist < 0.18:  # Increased from 0.1 — easier hands stacked detection
        return True, "Hands positioned correctly"
    return False, "Place one hand on top of the other"


def check_forward_reach(landmarks):
    """Check if the person is reaching forward toward the extended foot."""
    lw = landmarks[mp_pose_global.PoseLandmark.LEFT_WRIST.value]
    rw = landmarks[mp_pose_global.PoseLandmark.RIGHT_WRIST.value]
    hand_y = (lw.y + rw.y) / 2
    hand_x = (lw.x + rw.x) / 2

    lk = landmarks[mp_pose_global.PoseLandmark.LEFT_KNEE.value]
    rk = landmarks[mp_pose_global.PoseLandmark.RIGHT_KNEE.value]
    la = landmarks[mp_pose_global.PoseLandmark.LEFT_ANKLE.value]
    ra = landmarks[mp_pose_global.PoseLandmark.RIGHT_ANKLE.value]

    left_knee_angle  = calculate_angle_3d(
        landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value], lk, la)
    right_knee_angle = calculate_angle_3d(
        landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value], rk, ra)

    if left_knee_angle > right_knee_angle:
        extended_ankle = la
        extended_knee  = lk
    else:
        extended_ankle = ra
        extended_knee  = rk

    hands_below_knee = hand_y > extended_knee.y
    hands_near_foot  = abs(hand_x - extended_ankle.x) < 0.2

    if hands_below_knee and hands_near_foot:
        return True, "Reaching forward toward extended leg"
    return False, "Reach forward toward your extended foot"


# ─────────────────────────────────────────────────────────────────
# SEQUENTIAL POSITION VERIFICATION (runs 3 steps for sit-to-stand)
# ─────────────────────────────────────────────────────────────────
def check_arms_crossed_verification(landmarks):
    """Checks if arms are crossed on chest for sit-to-stand starting position."""
    try:
        ls = landmarks[mp_pose_global.PoseLandmark.LEFT_SHOULDER.value]
        rs = landmarks[mp_pose_global.PoseLandmark.RIGHT_SHOULDER.value]
        lw = landmarks[mp_pose_global.PoseLandmark.LEFT_WRIST.value]
        rw = landmarks[mp_pose_global.PoseLandmark.RIGHT_WRIST.value]
        sw = abs(ls.x - rs.x)
        lw_to_rs = math.sqrt((lw.x - rs.x)**2 + (lw.y - rs.y)**2)
        rw_to_ls = math.sqrt((rw.x - ls.x)**2 + (rw.y - ls.y)**2)
        if lw_to_rs < sw * 1.2 and rw_to_ls < sw * 1.2:
            return True, "Arms crossed correctly"
        return False, "Please cross both arms on your chest"
    except:
        return False, "Please cross both arms on your chest"
def run_position_verification(cap, pose, window_name="30-Second Chair Stand Test"):
    """
    Walks user through all 6 sit-and-reach positions sequentially.
    Each step must be held for 2 seconds to advance.
    Returns True when all steps pass, False if user presses Q.
    """
    steps = [
        ("Step 1: Position yourself fully in camera view",
             check_full_body),
        ("Step 2: Sit on the edge of the chair",
             check_sitting_position),
        ("Step 3: Place one foot flat on the floor",
             check_foot_flat_on_floor),
        ("Step 4: Extend one leg straight forward",
             check_leg_extended),
        ("Step 5: Place one hand on top of the other",
             check_hands_stacked),
        ("Step 6: Reach forward toward your extended foot",
             check_forward_reach),
    ]

    current_step = 0
    step_pass_start = None

    while current_step < len(steps):
        ret, frame = cap.read()
        if not ret:
            continue

        frame   = cv2.flip(frame, 1)
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        instruction, check_fn = steps[current_step]
        check_passed   = False
        status_message = ""

        if results.pose_landmarks:
            landmarks    = results.pose_landmarks.landmark
            check_passed, status_message = check_fn(landmarks)
        else:
            status_message = "No body detected! Step into the camera frame."

        # ── Progress bar showing how many steps done ──
        total = len(steps)
        bar_w = int((frame.shape[1] - 40) * (current_step / total))
        cv2.rectangle(frame, (20, frame.shape[0]-30),
                      (frame.shape[1]-20, frame.shape[0]-10), (50,50,50), -1)
        cv2.rectangle(frame, (20, frame.shape[0]-30),
                      (20 + bar_w, frame.shape[0]-10), (0,200,0), -1)
        cv2.putText(frame, f"Step {current_step+1} of {total}",
                    (20, frame.shape[0]-35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

        # ── Instruction text ──
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 45), (0,0,0), -1)
        cv2.putText(frame, instruction, (10, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        # ── Status text ──
        color = (0, 255, 0) if check_passed else (0, 0, 255)
        cv2.rectangle(frame, (0, 50), (frame.shape[1], 90), (0,0,0), -1)
        cv2.putText(frame, status_message, (10, 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        # ── Hold timer ──
        if check_passed:
            if step_pass_start is None:
                step_pass_start = time.time()
            held = time.time() - step_pass_start
            remaining = max(0, 2.0 - held)
            cv2.putText(frame, f"Hold for {remaining:.1f}s...", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            if held >= 2.0:
                current_step   += 1
                step_pass_start = None
        else:
            step_pass_start = None

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False

    # All 6 steps passed
    return True


# ─────────────────────────────────────────────────────────────────
# YOUR ORIGINAL CLASS — every method kept exactly as you wrote it
# Only run_test() has additions marked with # NEW
# ─────────────────────────────────────────────────────────────────
class SitToStandCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.stand_count = 0
        self.current_state = "sitting"
        self.test_duration = 30
        self.start_time = None
        self.test_started = False
        self.test_stopped = False
        self.last_change_time = 0
        self.COOLDOWN = 0.8
        self.arm_violation_count = 0
        self.arm_violation_threshold = 15
        self.scoring_norms = {
            'men': {
                '60-64': 14, '65-69': 12, '70-74': 12, '75-79': 11,
                '80-84': 10, '85-89': 8,  '90-94': 7
            },
            'women': {
                '60-64': 12, '65-69': 11, '70-74': 10, '75-79': 10,
                '80-84': 9,  '85-89': 8,  '90-94': 4
            }
        }
        self.seated_time = None
        self.auto_start_enabled = True
        self.countdown_done = False
        self.countdown_start = None
        self.countdown_duration = 3
        self.state_buffer = []
        self.required_frames = 10
        self.get_ready_start = None
        self.full_stand_reached = False
        self.session_history = []
        self.session_id = 1

    def is_user_seated(self, landmarks):
        try:
            left_hip   = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
            right_hip  = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y
            left_knee  = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y
            right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y
            hip_y  = (left_hip  + right_hip)  / 2
            knee_y = (left_knee + right_knee) / 2
            return knee_y > hip_y + 0.03
        except:
            return False

    def get_age_range(self, age):
        if 60 <= age <= 64:   return '60-64'
        elif 65 <= age <= 69: return '65-69'
        elif 70 <= age <= 74: return '70-74'
        elif 75 <= age <= 79: return '75-79'
        elif 80 <= age <= 84: return '80-84'
        elif 85 <= age <= 89: return '85-89'
        elif 90 <= age <= 94: return '90-94'
        else:                 return None

    def evaluate_score(self, count, age, gender):
        age_range = self.get_age_range(age)
        if age_range is None:
            return {'score': count, 'age_range': age_range,
                    'assessment': 'No norms available for this age'}
        gender_lower = gender.lower()
        if gender_lower not in ['men', 'women', 'male', 'female']:
            return {'score': count, 'age_range': age_range,
                    'assessment': 'Invalid gender specified'}
        gender_key = 'men' if gender_lower in ['male', 'men'] else 'women'
        threshold  = self.scoring_norms[gender_key][age_range]
        if count < threshold:
            assessment     = "Below expected range for age and sex"
            interpretation = (
                "This suggests weaker lower-body strength. "
                "Weaker leg strength may increase fall risk "
                "when combined with balance problems or prior falls."
            )
        else:
            assessment     = "Within or above expected range for age and sex"
            interpretation = "This suggests adequate lower-body strength for daily activities."
        return {
            'score': count, 'age_range': age_range, 'threshold': threshold,
            'assessment': assessment, 'interpretation': interpretation,
            'gender': gender_key.capitalize()
        }

    def print_final_report(self, count, age, gender, arm_violation=False):
        print("\n" + "="*70)
        print(" "*20 + "30-SECOND CHAIR STAND TEST")
        print(" "*25 + "FINAL RESULTS")
        print("="*70)
        result = self.evaluate_score(count, age, gender)
        print(f"\nPatient Information:")
        print(f"  Age: {age} years")
        print(f"  Gender: {result.get('gender', gender)}")
        print(f"  Age Range: {result['age_range']}")
        print(f"\nTest Results:")
        if arm_violation:
            print(f"  TEST STOPPED - Patient used arms to stand")
            print(f"  Total Stands: 0 (Protocol Violation)")
            print(f"\n  ⚠️  According to CDC STEADI protocol:")
            print(f"     'If the patient must use his/her arms to stand,")
            print(f"      stop the test. Record 0 for the number and score.'")
        else:
            print(f"  Total Stands in 30 seconds: {result['score']}")
            if 'threshold' in result:
                print(f"  Below Average Threshold: < {result['threshold']}")
            print(f"\nAssessment:")
            print(f"  {result['assessment']}")
            print(f"\nInterpretation:")
            print(f"  {result.get('interpretation', 'Interpretation not available.')}")
            print("\nNotes:")
            print("  • This test measures lower-body (leg) strength and functional mobility only.")
            print("  • It is a screening tool and should not be used alone to diagnose frailty or fall risk.")
            print("  • Balance is not directly measured in this test.")
            print("  • Interpret results with caution if balance felt unsteady, hands were used,")
            print("    or test conditions or camera setup were not ideal.")
            print("  • Consider sharing these results with a healthcare professional.")
        print("\n" + "-"*70)
        print("Reference: CDC STEADI - Stopping Elderly Accidents, Deaths & Injuries")
        print("="*70 + "\n")
        return result

    def record_session(self, age, gender, count, result, arm_violation):
        self.session_history.append({
            "session_id":    self.session_id,
            "timestamp":     time.strftime("%Y-%m-%d %H:%M:%S"),
            "age":           age,
            "gender":        gender,
            "count":         count,
            "arm_violation": arm_violation,
            "assessment":    result.get("assessment", "N/A")
        })
        self.session_id += 1

    def display_session_history(self):
        print("\n" + "=" * 70)
        print("SESSION HISTORY")
        print("=" * 70)
        for s in self.session_history:
            print(
                f"Session {s['session_id']} | {s['timestamp']} | "
                f"Age: {s['age']} | Gender: {s['gender']} | "
                f"Count: {s['count']} | "
                f"Arm Violation: {'YES' if s['arm_violation'] else 'NO'}"
            )
        print("=" * 70 + "\n")

    def prompt_retry_or_quit(self):
        while True:
            choice = input("Do you want to Retry (R) or Quit (Q)? ").strip().lower()
            if choice == 'r':   return True
            elif choice == 'q': return False
            else: print("Invalid input. Enter R or Q.")

    def reset_test_state(self):
        self.stand_count = 0
        self.current_state = "sitting"
        self.start_time = None
        self.test_started = False
        self.test_stopped = False
        self.arm_violation_count = 0
        self.last_change_time = 0
        self.seated_time = None
        self.state_buffer.clear()
        self.full_stand_reached = False

    def check_arm_usage(self, landmarks):
        try:
            left_shoulder  = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_wrist     = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_wrist    = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            left_hip       = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip      = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            left_wrist_to_right_shoulder = np.sqrt(
                (left_wrist.x  - right_shoulder.x)**2 +
                (left_wrist.y  - right_shoulder.y)**2)
            right_wrist_to_left_shoulder = np.sqrt(
                (right_wrist.x - left_shoulder.x)**2 +
                (right_wrist.y - left_shoulder.y)**2)
            left_wrist_below_hip  = left_wrist.y  > left_hip.y
            right_wrist_below_hip = right_wrist.y > right_hip.y
            shoulder_width        = abs(left_shoulder.x - right_shoulder.x)
            max_wrist_distance    = shoulder_width * 1.8
            return ((left_wrist_to_right_shoulder > max_wrist_distance or
                     right_wrist_to_left_shoulder > max_wrist_distance) or
                    (left_wrist_below_hip or right_wrist_below_hip))
        except Exception as e:
            print(f"Error checking arm usage: {e}")
            return False

    def are_arms_crossed(self, landmarks):
        try:
            left_shoulder  = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_wrist     = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_wrist    = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            lw_to_rs = np.sqrt((left_wrist.x  - right_shoulder.x)**2 +
                               (left_wrist.y  - right_shoulder.y)**2)
            rw_to_ls = np.sqrt((right_wrist.x - left_shoulder.x)**2 +
                               (right_wrist.y - left_shoulder.y)**2)
            max_dist = shoulder_width * 1.2
            return lw_to_rs < max_dist and rw_to_ls < max_dist
        except:
            return False

    def calculate_body_posture(self, landmarks):
        try:
            shoulder_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
            hip_y      = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
            knee_y     = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y +
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y) / 2
            torso_len   = abs(shoulder_y - hip_y)
            hip_to_knee = abs(hip_y - knee_y)
            if torso_len == 0:
                return self.current_state
            posture_score = hip_to_knee / torso_len
            if posture_score < 0.55:   return "sitting"
            elif posture_score > 0.70: return "standing"
            else:                      return "transition"
        except:
            return self.current_state

    def is_fully_standing(self, landmarks):
        hip_y      = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
        knee_y     = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y +
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y) / 2
        shoulder_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
        torso_len  = abs(shoulder_y - hip_y)
        return hip_y < knee_y - (torso_len * 0.3)

    def update_count(self, new_state, landmarks):
        current_time = time.time()
        if new_state == "transition":
            return
        if new_state == "standing" and self.current_state != "standing":
            if self.is_fully_standing(landmarks) and current_time - self.last_change_time > self.COOLDOWN:
                self.current_state = "standing"
                if not self.full_stand_reached:
                    self.full_stand_reached = True
                    print("[DEBUG] Full stand confirmed")
                self.last_change_time = current_time
        if new_state == "sitting" and self.current_state == "standing" and self.full_stand_reached:
            if current_time - self.last_change_time > self.COOLDOWN:
                self.stand_count   += 1
                self.current_state  = "sitting"
                self.full_stand_reached = False
                self.last_change_time   = current_time
                print(f"✅ Rep completed! Count = {self.stand_count}")

    def get_patient_info(self):
        print("\n" + "="*70)
        print("Please enter patient information for scoring:")
        print("="*70)
        while True:
            try:
                age = int(input("Enter patient age (60-94): "))
                if age < 0:
                    print("Age must be positive. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        while True:
            gender = input("Enter patient gender (Male/Female or M/F): ").strip().lower()
            if gender in ['male', 'female', 'm', 'f', 'men', 'women']:
                if gender == 'm':   gender = 'male'
                elif gender == 'f': gender = 'female'
                break
            else:
                print("Invalid input. Please enter Male/Female or M/F.")
        return age, gender

    def show_result_overlay(self, cap, final_result, test_status):
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            title_text  = "TEST COMPLETE" if test_status == "completed" else "TEST FAILED"
            title_color = (0, 255, 0)     if test_status == "completed" else (0, 0, 255)
            cv2.putText(frame, title_text, (40, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.6, title_color, 3)
            cv2.putText(frame, f"Total Stands: {self.stand_count}", (40, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 0), 2)
            cv2.putText(frame, "Result:", (40, 165),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(frame, final_result.get('assessment', 'Result not available'),
                        (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 255, 200), 2)
            cv2.putText(frame, "This test measures leg strength only and is not a diagnosis.",
                        (40, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
            cv2.putText(frame, "SESSION HISTORY", (40, 270),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            y_offset = 310
            s    = self.session_history[-1]
            text = (
                f"Session {len(self.session_history)} | {s['timestamp']} | "
                f"Age: {s['age']} | Gender: {s['gender']} | "
                f"Count: {s['count']} | "
                f"Arm Violation: {'YES' if s['arm_violation'] else 'NO'}"
            )
            cv2.putText(frame, text, (40, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
            cv2.putText(frame, "Press R to Retry or Q to Quit",
                        (40, y_offset + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.imshow("30-Second Chair Stand Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('r'), ord('R')): return True
            elif key in (ord('q'), ord('Q')): return False

    def run_test(self):
        """Main function to run the 30-second chair stand test with retry loop"""

        age, gender = self.get_patient_info()

        # NEW: Show instruction screen once before first run
        show_instruction_screen()

        while True:  # Retry loop

            frame_skip  = 2
            frame_count = 0

            # Auto Select Camera
            for i in range(5):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    print(f"Camera found at index {i}")
                    break
                cap.release()
            else:
                print("No camera found in indices 0-4")
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cv2.namedWindow("30-Second Chair Stand Test", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("30-Second Chair Stand Test",
                                  cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # NEW: Run all 6 position verification steps before the test
            print("Starting position verification...")
            all_passed = run_position_verification(
                cap, self.pose, "30-Second Chair Stand Test"
            )
            if not all_passed:
                cap.release()
                cv2.destroyAllWindows()
                self.pose.close()
                return

            # Wait for correct starting position (your original logic)
            start_auto = False
            self.reset_test_state()

            while not start_auto:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue
                frame   = cv2.flip(frame, 1)
                results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                seated = arms_crossed = knees_visible = False
                if results.pose_landmarks:
                    landmarks    = results.pose_landmarks.landmark
                    seated       = self.is_user_seated(landmarks)
                    arms_crossed = self.are_arms_crossed(landmarks)
                    try:
                        lk = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
                        rk = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility
                        knees_visible = lk > 0.6 and rk > 0.6
                    except:
                        knees_visible = False

                cv2.putText(frame, "30-SECOND CHAIR STAND TEST", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.putText(frame,
                            "Measures leg strength only. Use a stable chair.",
                            (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                cv2.putText(frame, "Get into starting position:", (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                y = 150
                if not seated:
                    cv2.putText(frame, "• Please sit properly on the chair",
                                (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    y += 40
                if seated and not arms_crossed:
                    cv2.putText(frame, "• Please cross your arms on your chest",
                                (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    y += 40
                if seated and not knees_visible:
                    cv2.putText(frame, "• Ensure knees are visible to the camera",
                                (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    y += 40
                if seated and arms_crossed and knees_visible:
                    cv2.putText(frame, "Good position! Starting countdown...",
                                (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)
                    start_auto = True
                    self.countdown_start = time.time()

                cv2.imshow("30-Second Chair Stand Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    self.pose.close()
                    return

            # NEW: Audible 3-2-1-GO countdown
            play_audible_countdown(cap, "30-Second Chair Stand Test")

            # Main 30-second test loop (your original logic — unchanged)
            self.start_time   = time.time()
            self.test_started = True

            while self.test_started and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    continue
                frame   = cv2.flip(frame, 1)
                results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if not results.pose_landmarks:
                    cv2.imshow("30-Second Chair Stand Test", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue

                landmarks = results.pose_landmarks.landmark

                arm_violation = self.check_arm_usage(landmarks)
                if arm_violation:
                    self.arm_violation_count += 1
                else:
                    self.arm_violation_count = 0

                if self.arm_violation_count >= self.arm_violation_threshold:
                    self.test_stopped = True
                    self.test_started = False
                    result = self.evaluate_score(0, age, gender)
                    self.record_session(age, gender, 0, result, arm_violation=True)
                    self.print_final_report(0, age, gender, arm_violation=True)
                    retry = self.show_result_overlay(cap, result, test_status="failed")
                    if retry:
                        self.reset_test_state()
                        break
                    else:
                        self.display_session_history()
                        self.pose.close()
                        cap.release()
                        cv2.destroyAllWindows()
                        return

                new_state = self.calculate_body_posture(landmarks)
                self.update_count(new_state, landmarks)

                elapsed_time   = time.time() - self.start_time
                remaining_time = max(0, self.test_duration - elapsed_time)

                if remaining_time <= 0:
                    self.test_started = False
                    result = self.evaluate_score(self.stand_count, age, gender)
                    self.record_session(age, gender, self.stand_count, result, arm_violation=False)
                    self.print_final_report(self.stand_count, age, gender, arm_violation=False)
                    retry = self.show_result_overlay(cap, result, test_status="completed")
                    if retry:
                        self.reset_test_state()
                        break
                    else:
                        self.display_session_history()
                        self.pose.close()
                        cap.release()
                        cv2.destroyAllWindows()
                        return

                cv2.putText(frame, f"Count: {self.stand_count}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.putText(frame, f"Time: {remaining_time:.1f}s", (10, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                if self.test_stopped:
                    cv2.putText(frame, "TEST STOPPED", (10, 130),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow("30-Second Chair Stand Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    counter = SitToStandCounter()
    counter.run_test()