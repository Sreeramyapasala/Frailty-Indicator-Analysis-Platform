import cv2
import time
import numpy as np
import mediapipe as mp
import pygame
import os
import sys
import math

# ─────────────────────────────────────────────────────────────────
# PM STYLE GUIDE — BGR colors
# ─────────────────────────────────────────────────────────────────
C_PRIMARY    = (58,  107,  11)
C_SECONDARY  = (74,  166,  16)
C_BG         = (255, 255, 255)
C_SURFACE    = (236, 244, 231)
C_TEXT       = (31,   31,  31)
C_MUTED      = (128, 114, 107)
C_BORDER     = (217, 217, 217)
C_WHITE      = (255, 255, 255)
C_WARNING_BG = (0,   100, 200)
C_DANGER_BG  = (0,    60, 180)
C_ERROR      = (60,   80, 255)

FH = cv2.FONT_HERSHEY_DUPLEX
FB = cv2.FONT_HERSHEY_SIMPLEX


# ─────────────────────────────────────────────────────────────────
# STYLE HELPERS
# ─────────────────────────────────────────────────────────────────
def filled_rect(img, x1, y1, x2, y2, fill, border=None, thickness=2):
    cv2.rectangle(img, (x1, y1), (x2, y2), fill, -1)
    if border:
        cv2.rectangle(img, (x1, y1), (x2, y2), border, thickness)


def primary_button(img, x1, y1, x2, y2, text, font_scale=0.7):
    filled_rect(img, x1, y1, x2, y2, C_SECONDARY, C_PRIMARY, 2)
    tw, th = cv2.getTextSize(text, FH, font_scale, 1)[0]
    cv2.putText(img, text,
                (x1 + (x2-x1-tw)//2, y1 + (y2-y1+th)//2),
                FH, font_scale, C_WHITE, 1)


def secondary_button(img, x1, y1, x2, y2, text, font_scale=0.7):
    filled_rect(img, x1, y1, x2, y2, C_BG, C_PRIMARY, 2)
    tw, th = cv2.getTextSize(text, FH, font_scale, 1)[0]
    cv2.putText(img, text,
                (x1 + (x2-x1-tw)//2, y1 + (y2-y1+th)//2),
                FH, font_scale, C_PRIMARY, 1)


def status_chip(img, x, y, text, ok):
    bg  = C_SECONDARY if ok else C_ERROR
    bdr = C_PRIMARY   if ok else (30, 40, 180)
    tw, th = cv2.getTextSize(text, FB, 0.55, 1)[0]
    pad = 6
    filled_rect(img, x, y, x+tw+pad*2, y+th+pad*2, bg, bdr, 1)
    cv2.putText(img, text, (x+pad, y+th+pad), FB, 0.55, C_WHITE, 1)


def progress_bar(img, x1, y, x2, frac, h=12):
    filled_rect(img, x1, y, x2, y+h, C_BORDER)
    if frac > 0:
        filled_rect(img, x1, y,
                    x1+int((x2-x1)*min(frac,1.0)), y+h, C_SECONDARY)


def wrap_text(text, max_chars=55):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur)+len(w)+1 <= max_chars:
            cur = (cur+" "+w).strip()
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


# ─────────────────────────────────────────────────────────────────
# AUDIO SETUP
# ─────────────────────────────────────────────────────────────────
sys.path.append('.')
pygame.mixer.init()

AUDIO_MAP = {
    'basic_intro':    'audio/audiobasic_intro.mp3',
    'basic_1':        'audio/audiobasic_1.mp3',
    'basic_2':        'audio/audiobasic_2.mp3',
    'basic_3':        'audio/audiobasic_3.mp3',
    'basic_4':        'audio/audiobasic_4.mp3',
    'basic_5':        'audio/audiobasic_5.mp3',
    'basic_6':        'audio/audiobasic_6.mp3',
    'basic_ready':    'audio/audiobasic_ready.mp3',
    'test_intro':     'audio/audiotest_intro.mp3',
    'test_1':         'audio/audiotest_1.mp3',
    'test_2':         'audio/audiotest_2.mp3',
    'test_3':         'audio/audiotest_3.mp3',
    'test_4':         'audio/audiotest_4.mp3',
    'test_5':         'audio/audiotest_5.mp3',
    'test_6':         'audio/audiotest_6.mp3',
    'test_7':         'audio/audiotest_7.mp3',
    'test_confirmed': 'audio/audiotest_confirmed.mp3',
    'countdown_3':    'audio/audiocountdown_3.mp3',
    'countdown_2':    'audio/audiocountdown_2.mp3',
    'countdown_1':    'audio/audiocountdown_1.mp3',
    'countdown_go':   'audio/audiocountdown_go.mp3',
    'test_complete':  'audio/audiotest_complete.mp3',
    'test_stopped':   'audio/audiotest_stopped.mp3',
}


def play_audio_nonblocking(key):
    path = AUDIO_MAP.get(key, '')
    if not path or not os.path.exists(path):
        print(f"[Audio] Missing: {key} -> {path}")
        return False
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        time.sleep(0.1)
        return True
    except Exception as e:
        print(f"[Audio] Error: {e}")
        return False


def wait_for_key_or_audio_end(frame, win, timeout=30.0):
    start = time.time()
    while time.time() - start < timeout:
        cv2.imshow(win, frame)
        k = cv2.waitKey(50)
        if k != -1:
            pygame.mixer.music.stop()
            return True
        if not pygame.mixer.music.get_busy():
            return False
    pygame.mixer.music.stop()
    return False


def speak(key):
    path = AUDIO_MAP.get(key, '')
    if not path or not os.path.exists(path):
        print(f"[Audio] Missing: {key} -> {path}")
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
    except Exception as e:
        print(f"[Audio] Error: {e}")


# ─────────────────────────────────────────────────────────────────
# SCREEN 1 — BASIC INSTRUCTIONS (same as original)
# ─────────────────────────────────────────────────────────────────
BASIC_INSTRUCTIONS = [
    "Find a bright, quiet spot! Good lighting helps the camera see you clearly.",
    "Avoid distractions! No phone calls, deliveries, or interruptions during the test.",
    "Check that your camera is on, working and clearly focused. Place your laptop or camera in a stable position and do not hold it in your hand.",
    "Stay in the camera frame the whole time. Make sure you don't move out of view!",
    "Wear comfortable and fitted clothing so your body movements are clearly visible.",
    "Clear the space around you. Make sure there is enough room to move freely!",
]

def show_basic_instructions(image_path="basic_instructions.png"):
    WIN = "Before You Start"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    img = cv2.imread(os.path.join(os.getcwd(), image_path))
    if img is None:
        print(f"[Info] {image_path} not found — text fallback.")
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 255
        filled_rect(img, 0, 0, 1280, 80, C_PRIMARY)
        cv2.putText(img, "Before You Start", (40, 54), FH, 1.4, C_WHITE, 2)
        y = 100
        for i, line in enumerate(BASIC_INSTRUCTIONS, 1):
            card = C_SURFACE if i % 2 == 0 else C_BG
            filled_rect(img, 30, y, 1250, y+75, card, C_BORDER, 1)
            filled_rect(img, 40, y+16, 78, y+54, C_SECONDARY)
            cv2.putText(img, str(i), (50, y+44), FH, 0.75, C_WHITE, 1)
            ty = y + 32
            for wl in wrap_text(line, 90):
                cv2.putText(img, wl, (92, ty), FB, 0.72, C_TEXT, 1)
                ty += 26
            y += 90

    # fit image preserving aspect ratio — no stretching
    canvas_w, canvas_h = 1280, 650  # leave 70px at bottom for bar
    fitted = fit_image_on_canvas(img, canvas_w, canvas_h, (245, 245, 245))

    # build full canvas with bottom bar
    full = np.ones((720, 1280, 3), dtype=np.uint8)
    full[:] = (245, 245, 245)
    full[0:canvas_h, 0:canvas_w] = fitted
    filled_rect(full, 0, canvas_h, 1280, 720, C_PRIMARY)
    img = full
    cv2.imshow(WIN, img)
    cv2.waitKey(1)
    play_audio_nonblocking('basic_intro')
    wait_for_key_or_audio_end(img, WIN)

    audio_keys = ['basic_1','basic_2','basic_3','basic_4','basic_5','basic_6']
    for i, key in enumerate(audio_keys, 1):
        display = img.copy()
        filled_rect(display, 0, 648, 1280, 720, C_PRIMARY)
        progress_bar(display, 20, 655, 1260, i/len(audio_keys), h=10)
        cv2.putText(display,
                    f"Instruction {i} of {len(audio_keys)}  press any key to skip",
                    (40, 700), FB, 0.72, C_WHITE, 1)
        cv2.imshow(WIN, display)
        cv2.waitKey(1)
        play_audio_nonblocking(key)
        skipped = wait_for_key_or_audio_end(display, WIN)
        if not skipped:
            deadline = time.time() + 0.8
            while time.time() < deadline:
                cv2.imshow(WIN, display)
                if cv2.waitKey(50) != -1:
                    break

    final = img.copy()
    filled_rect(final, 0, 648, 1280, 720, C_PRIMARY)
    progress_bar(final, 20, 655, 1260, 1.0, h=10)
    primary_button(final, 380, 660, 900, 710,
                   "Press any key to continue", 0.65)
    cv2.imshow(WIN, final)
    cv2.waitKey(1)
    play_audio_nonblocking('basic_ready')
    wait_for_key_or_audio_end(final, WIN, timeout=8.0)

    cv2.destroyWindow(WIN)
    time.sleep(0.5)
    print("Basic instructions done!")


# ─────────────────────────────────────────────────────────────────
# SCREEN 2 — TEST INSTRUCTIONS (NO CAMERA VERIFICATION)
# Shows full image on left, instruction text on right
# Audio plays for each slide, user presses any key to advance
# ─────────────────────────────────────────────────────────────────
TEST_SLIDES_INFO = [
    ("Step 1 of 7 — Starting position",
     "Sit at the FRONT EDGE of the chair.\nBack straight. Feet flat on the floor.",
     "test_1"),
    ("Step 2 of 7 — Foot placement",
     "Keep your feet SHOULDER-WIDTH apart.\nDo NOT move or reposition them during the test.",
     "test_2"),
    ("Step 3 of 7 — Arms position",
     "Cross your arms OVER YOUR CHEST.\nKeep them there throughout the entire test.",
     "test_3"),
    ("Step 4 of 7 — How to stand",
     "Stand up FULLY until hips and knees are straight.\nThen sit back down in a controlled way.",
     "test_4"),
    ("Step 5 of 7 — What counts as a rep",
     "Each rep = full SIT -> STAND -> SIT.\nBoth phases must be complete to count.",
     "test_5"),
    ("Step 6 of 7 — Do NOT use your arms",
     "Do NOT use your hands or arms to push off.\nThe test will STOP AUTOMATICALLY if you do.",
     "test_6"),
    ("Step 7 of 7 — Timer",
     "Follow the on-screen timer.\nContinue until the 30-second test is complete.",
     "test_7"),
]


def fit_image_on_canvas(img, canvas_w, canvas_h, bg_color=(245, 245, 245)):
    """
    Fit image onto canvas while preserving aspect ratio.
    Adds padding around image so it is never stretched.
    """
    canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8)
    canvas[:] = bg_color

    ih, iw = img.shape[:2]
    scale  = min(canvas_w / iw, canvas_h / ih)
    new_w  = int(iw * scale)
    new_h  = int(ih * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # center on canvas
    x_off = (canvas_w - new_w) // 2
    y_off = (canvas_h - new_h) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
    return canvas


def _draw_info_slide(slide_img, header, body, slide_idx, total_slides, w=1280, h=720):
    """
    Draw fullscreen instruction slide.
    Full image shown preserving aspect ratio.
    Small overlay bar at bottom shows step info.
    No split screen.
    """
    bar_h = 90  # bottom bar height

    # canvas = light gray background
    frame = np.ones((h, w, 3), dtype=np.uint8)
    frame[:] = (245, 245, 245)

    # ── show full instruction image, aspect-ratio preserved ───────
    if slide_img is not None:
        fitted = fit_image_on_canvas(slide_img, w, h - bar_h, (245, 245, 245))
        frame[0:h-bar_h, 0:w] = fitted

    # ── bottom overlay bar ────────────────────────────────────────
    filled_rect(frame, 0, h-bar_h, w, h, C_PRIMARY)

    # step label on left
    hdr_parts = header.split(" — ")
    step_label = hdr_parts[0] if len(hdr_parts) == 2 else header
    sub_label  = hdr_parts[1] if len(hdr_parts) == 2 else ""
    cv2.putText(frame, step_label,
                (16, h-bar_h+28), FH, 0.75, C_WHITE, 1)
    if sub_label:
        cv2.putText(frame, sub_label,
                    (16, h-bar_h+55), FB, 0.62, (200, 240, 200), 1)

    # hint on right
    hint = "Press any key to continue  |  waiting for audio..."
    hw   = cv2.getTextSize(hint, FB, 0.55, 1)[0][0]
    cv2.putText(frame, hint,
                (w - hw - 16, h-bar_h+28), FB, 0.55, (200, 240, 200), 1)

    # progress bar at very bottom
    progress_bar(frame, 0, h-8, w,
                 (slide_idx+1)/total_slides, h=8)

    # step dots above progress bar
    dot_y = h - bar_h//2 + 10
    sp    = 26
    sx    = w - total_slides*sp - 20
    for i in range(total_slides):
        col = C_SECONDARY if i < slide_idx else \
              C_PRIMARY   if i == slide_idx else (100, 140, 60)
        r   = 9 if i == slide_idx else 6
        cv2.circle(frame, (sx + i*sp, dot_y), r, col, -1)
        if i == slide_idx:
            cv2.circle(frame, (sx + i*sp, dot_y), r, C_WHITE, 1)

    return frame


def show_test_instructions_display_only(image_path="test_instructions.png"):
    """
    Shows test instructions as a simple slideshow.
    No camera. No position verification.
    Each slide plays audio then waits for keypress or auto-advances.
    """
    WIN = "30-Second Chair Stand Test"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # load instruction image once
    raw = cv2.imread(os.path.join(os.getcwd(), image_path))
    if raw is None:
        print(f"[Info] {image_path} not found — left panel will be blank.")

    total = len(TEST_SLIDES_INFO)

    # play intro once
    speak('test_intro')

    for idx, (header, body, audio_key) in enumerate(TEST_SLIDES_INFO):
        # build slide frame
        slide = _draw_info_slide(raw, header, body, idx, total)

        # show slide
        cv2.imshow(WIN, slide)
        cv2.waitKey(1)

        # play audio non-blocking, wait for finish or keypress
        play_audio_nonblocking(audio_key)
        skipped = wait_for_key_or_audio_end(slide, WIN, timeout=15.0)

        # if not skipped, short pause then auto-advance
        if not skipped:
            deadline = time.time() + 1.0
            while time.time() < deadline:
                cv2.imshow(WIN, slide)
                if cv2.waitKey(50) != -1:
                    break

    # final confirmation
    speak('test_confirmed')
    time.sleep(0.4)
    return True


# ─────────────────────────────────────────────────────────────────
# AUDIBLE COUNTDOWN
# ─────────────────────────────────────────────────────────────────
def play_audible_countdown(cap, window_name="30-Second Chair Stand Test"):
    keys   = ['countdown_3','countdown_2','countdown_1','countdown_go']
    labels = ["3", "2", "1", "GO!"]
    colors = [C_MUTED, C_MUTED, C_SECONDARY, C_PRIMARY]

    for step in range(4):
        speak(keys[step])
        deadline = time.time() + 1.5
        while time.time() < deadline:
            ret, frame = cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]
            overlay = frame.copy()
            cv2.rectangle(overlay, (0,0), (w,h), (20,20,20), -1)
            cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
            txt  = labels[step]
            size = cv2.getTextSize(txt, FH, 5, 6)[0]
            tx   = (w - size[0]) // 2
            ty   = (h + size[1]) // 2
            cv2.putText(frame, txt, (tx+3, ty+3), FH, 5, C_TEXT, 6)
            cv2.putText(frame, txt, (tx, ty),     FH, 5, colors[step], 6)
            sub = "GET READY" if step < 3 else "START NOW!"
            sw2 = cv2.getTextSize(sub, FB, 0.9, 2)[0]
            cv2.putText(frame, sub, ((w-sw2[0])//2, ty+60), FB, 0.9, C_WHITE, 2)
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)


# ─────────────────────────────────────────────────────────────────
# EDGE CASE 1 — POOR LIGHTING
# ─────────────────────────────────────────────────────────────────
def check_lighting(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if float(np.mean(gray)) < 60:
        return True, "Low lighting! Please turn on a light."
    top    = float(np.mean(gray[0:h//4,      w//4:3*w//4]))
    centre = float(np.mean(gray[h//4:3*h//4, w//4:3*w//4]))
    if top > centre + 80 and top > 180:
        return True, "Backlit! Move away from the window."
    return False, ""


# ─────────────────────────────────────────────────────────────────
# EDGE CASE 2 — MULTIPLE PEOPLE
# ─────────────────────────────────────────────────────────────────
def check_multiple_people(frame):
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    rects, _ = hog.detectMultiScale(
        cv2.resize(frame, (320, 240)),
        winStride=(8,8), padding=(4,4), scale=1.05)
    c = len(rects)
    return c > 1, c


# ─────────────────────────────────────────────────────────────────
# WARNING BADGES
# ─────────────────────────────────────────────────────────────────
def draw_warnings(frame, lighting_bad, lighting_msg,
                  multi_people, people_count):
    h, w     = frame.shape[:2]
    y_offset = 60

    def badge(text, bg):
        nonlocal y_offset
        (tw, th), _ = cv2.getTextSize(text, FB, 0.55, 1)
        pad = 7
        x1 = w - tw - pad*2 - 12
        y2 = y_offset + th + pad*2
        filled_rect(frame, x1, y_offset, w-12, y2, bg, C_WHITE, 1)
        cv2.putText(frame, text, (x1+pad, y2-pad), FB, 0.55, C_WHITE, 1)
        y_offset = y2 + 5

    if lighting_bad:
        badge(f"! {lighting_msg}", C_WARNING_BG)
    if multi_people:
        badge(f"! {people_count} people in frame - ask others to step out",
              C_DANGER_BG)


# ─────────────────────────────────────────────────────────────────
# MAIN CLASS
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
        self.stand_count             = 0
        self.current_state           = "sitting"
        self.test_duration           = 30
        self.start_time              = None
        self.test_started            = False
        self.test_stopped            = False
        self.last_change_time        = 0
        self.COOLDOWN                = 0.8
        self.arm_violation_count     = 0
        self.arm_violation_threshold = 15
        self.scoring_norms = {
            'men':   {'60-64':14,'65-69':12,'70-74':12,'75-79':11,
                      '80-84':10,'85-89':8, '90-94':7},
            'women': {'60-64':12,'65-69':11,'70-74':10,'75-79':10,
                      '80-84':9, '85-89':8, '90-94':4}
        }
        self.seated_time         = None
        self.auto_start_enabled  = True
        self.countdown_done      = False
        self.countdown_start     = None
        self.countdown_duration  = 3
        self.state_buffer        = []
        self.required_frames     = 10
        self.get_ready_start     = None
        self.full_stand_reached  = False
        self.session_history     = []
        self.session_id          = 1
        self._multi_people       = False
        self._people_count       = 1

    def is_user_seated(self, landmarks):
        try:
            lh = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
            rh = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y
            lk = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y
            rk = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y
            return (lk+rk)/2 > (lh+rh)/2 + 0.03
        except:
            return False

    def get_age_range(self, age):
        if   60 <= age <= 64: return '60-64'
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
            return {'score':count,'age_range':None,
                    'assessment':'No norms available for this age'}
        gk = 'men' if gender.lower() in ['male','men','m'] else 'women'
        if gender.lower() not in ['men','women','male','female','m','f']:
            return {'score':count,'age_range':age_range,
                    'assessment':'Invalid gender specified'}
        threshold = self.scoring_norms[gk][age_range]
        if count < threshold:
            assessment     = "Below expected range for age and sex"
            interpretation = ("This suggests weaker lower-body strength. "
                "Weaker leg strength may increase fall risk "
                "when combined with balance problems or prior falls.")
        else:
            assessment     = "Within or above expected range for age and sex"
            interpretation = ("This suggests adequate lower-body strength "
                              "for daily activities.")
        return {'score':count,'age_range':age_range,'threshold':threshold,
                'assessment':assessment,'interpretation':interpretation,
                'gender':gk.capitalize()}

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
            print(f"\n  According to CDC STEADI protocol:")
            print(f"     If the patient must use arms to stand,")
            print(f"     stop the test. Record 0 for the number and score.")
        else:
            print(f"  Total Stands in 30 seconds: {result['score']}")
            if 'threshold' in result:
                print(f"  Below Average Threshold: < {result['threshold']}")
            print(f"\nAssessment:")
            print(f"  {result['assessment']}")
            print(f"\nInterpretation:")
            print(f"  {result.get('interpretation','Interpretation not available.')}")
            print("\nNotes:")
            print("  This test measures lower-body (leg) strength and functional mobility only.")
            print("  It is a screening tool and should not be used alone to diagnose frailty.")
            print("  Balance is not directly measured in this test.")
            print("  Interpret results with caution if balance felt unsteady, hands were used,")
            print("  or test conditions or camera setup were not ideal.")
            print("  Consider sharing these results with a healthcare professional.")
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
            "assessment":    result.get("assessment","N/A")
        })
        self.session_id += 1

    def display_session_history(self):
        print("\n" + "="*70)
        print("SESSION HISTORY")
        print("="*70)
        for s in self.session_history:
            print(
                f"Session {s['session_id']} | {s['timestamp']} | "
                f"Age: {s['age']} | Gender: {s['gender']} | "
                f"Count: {s['count']} | "
                f"Arm Violation: {'YES' if s['arm_violation'] else 'NO'}"
            )
        print("="*70 + "\n")

    def prompt_retry_or_quit(self):
        while True:
            choice = input("Do you want to Retry (R) or Quit (Q)? ").strip().lower()
            if choice == 'r':   return True
            elif choice == 'q': return False
            else: print("Invalid input. Enter R or Q.")

    def reset_test_state(self):
        self.stand_count         = 0
        self.current_state       = "sitting"
        self.start_time          = None
        self.test_started        = False
        self.test_stopped        = False
        self.arm_violation_count = 0
        self.last_change_time    = 0
        self.seated_time         = None
        self.state_buffer.clear()
        self.full_stand_reached  = False
        self._multi_people       = False
        self._people_count       = 1

    def check_arm_usage(self, landmarks):
        try:
            ls = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            rs = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            lw = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            rw = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            lh = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            rh = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            sw = abs(ls.x - rs.x)
            lw_to_rs = np.sqrt((lw.x-rs.x)**2+(lw.y-rs.y)**2)
            rw_to_ls = np.sqrt((rw.x-ls.x)**2+(rw.y-ls.y)**2)
            return ((lw_to_rs > sw*1.8 or rw_to_ls > sw*1.8) or
                    (lw.y > lh.y or rw.y > rh.y))
        except Exception as e:
            print(f"Error checking arm usage: {e}")
            return False

    def are_arms_crossed(self, landmarks):
        try:
            ls = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            rs = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            lw = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            rw = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            sw = abs(ls.x - rs.x)
            return (np.sqrt((lw.x-rs.x)**2+(lw.y-rs.y)**2) < sw*1.2 and
                    np.sqrt((rw.x-ls.x)**2+(rw.y-ls.y)**2) < sw*1.2)
        except:
            return False

    def calculate_body_posture(self, landmarks):
        try:
            sh_y  = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)/2
            hip_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y)/2
            kn_y  = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y +
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y)/2
            torso = abs(sh_y - hip_y)
            if torso == 0: return self.current_state
            score = abs(hip_y - kn_y) / torso
            if score < 0.55:   return "sitting"
            elif score > 0.70: return "standing"
            else:              return "transition"
        except:
            return self.current_state

    def is_fully_standing(self, landmarks):
        hip_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                 landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y)/2
        kn_y  = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y +
                 landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y)/2
        sh_y  = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                 landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)/2
        return hip_y < kn_y - (abs(sh_y-hip_y)*0.3)

    def update_count(self, new_state, landmarks):
        now = time.time()
        if new_state == "transition": return
        if new_state == "standing" and self.current_state != "standing":
            if (self.is_fully_standing(landmarks) and
                    now - self.last_change_time > self.COOLDOWN):
                self.current_state = "standing"
                if not self.full_stand_reached:
                    self.full_stand_reached = True
                    print("[DEBUG] Full stand confirmed")
                self.last_change_time = now
        if (new_state == "sitting" and self.current_state == "standing"
                and self.full_stand_reached):
            if now - self.last_change_time > self.COOLDOWN:
                self.stand_count       += 1
                self.current_state      = "sitting"
                self.full_stand_reached = False
                self.last_change_time   = now
                print(f"Rep completed! Count = {self.stand_count}")

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
            if gender in ['male','female','m','f','men','women']:
                if gender == 'm': gender = 'male'
                elif gender == 'f': gender = 'female'
                break
            print("Invalid input. Please enter Male/Female or M/F.")
        return age, gender

    def show_result_overlay(self, cap, final_result, test_status):
        while True:
            ret, frame = cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            overlay = frame.copy()
            cv2.rectangle(overlay, (0,0), (w,h), (10,10,10), -1)
            cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

            cx  = int(w * 0.08)
            cy  = int(h * 0.05)
            cw  = int(w * 0.84)
            ch  = int(h * 0.90)
            cx2 = cx + cw
            cy2 = cy + ch

            filled_rect(frame, cx, cy, cx2, cy2, C_BG, C_BORDER, 2)

            hdr_h   = int(ch * 0.12)
            hdr_col = C_PRIMARY if test_status == "completed" else C_ERROR
            filled_rect(frame, cx, cy, cx2, cy+hdr_h, hdr_col)
            title = "TEST COMPLETE" if test_status == "completed" else "TEST STOPPED"
            ts = cv2.getTextSize(title, FH, 1.4, 2)[0]
            cv2.putText(frame, title,
                        (cx + (cw-ts[0])//2, cy+hdr_h-14),
                        FH, 1.4, C_WHITE, 2)

            def card_text(text, y, font, scale, color, thickness=1):
                pad   = 24
                max_w = cw - pad*2
                s     = scale
                while cv2.getTextSize(text, font, s, thickness)[0][0] > max_w \
                        and s > 0.35:
                    s -= 0.05
                cv2.putText(frame, text, (cx+pad, y), font, s, color, thickness)
                return int(cv2.getTextSize(text, font, s, thickness)[0][1]*1.6)

            ty = cy + hdr_h + 28
            line_h = card_text(f"Total Stands:  {self.stand_count}",
                               ty, FH, 1.0, C_TEXT, 2)
            ty += line_h + 10
            cv2.line(frame, (cx+16, ty), (cx2-16, ty), C_BORDER, 1)
            ty += 18

            assess = final_result.get('assessment', 'N/A')
            test_w = cv2.getTextSize("W"*40, FB, 0.72, 1)[0][0]
            max_c  = int(40*(cw-48)/max(test_w,1))
            for ln in wrap_text(assess, max(20, max_c)):
                lh2 = card_text(ln, ty, FB, 0.72, C_TEXT)
                ty += lh2

            ty += 6
            card_text("This test measures leg strength only and is not a diagnosis.",
                      ty, FB, 0.58, C_MUTED)
            ty += 28
            cv2.line(frame, (cx+16, ty), (cx2-16, ty), C_BORDER, 1)
            ty += 16

            if self.session_history:
                s = self.session_history[-1]
                card_text(
                    f"Session {len(self.session_history)}  |  "
                    f"Age: {s['age']}  |  Gender: {s['gender']}",
                    ty, FB, 0.58, C_MUTED)
                ty += 26
                card_text(
                    f"Count: {s['count']}  |  "
                    f"Arm violation: {'YES' if s['arm_violation'] else 'NO'}",
                    ty, FB, 0.58, C_MUTED)
                ty += 30

            btn_y = cy2 - 68
            btn_w = (cw - 48) // 2
            primary_button(frame,
                           cx+16, btn_y, cx+16+btn_w, btn_y+52,
                           "R  -  Retry", 0.75)
            secondary_button(frame,
                             cx+32+btn_w, btn_y, cx2-16, btn_y+52,
                             "Q  -  Quit", 0.75)

            cv2.imshow("30-Second Chair Stand Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('r'), ord('R')): return True
            if key in (ord('q'), ord('Q')): return False

    # ─────────────────────────────────────────────────────────────
    # RUN TEST
    # ─────────────────────────────────────────────────────────────
    def run_test(self):
        """Main function — test instructions shown as display only, no verification."""

        age, gender = self.get_patient_info()

        # Screen 1: basic instructions
        show_basic_instructions(image_path="basic_instructions.png")

        while True:  # retry loop

            frame_skip  = 2
            frame_count = 0

            for i in range(5):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    print(f"Camera found at index {i}")
                    break
                cap.release()
            else:
                print("No camera found in indices 0-4")
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cv2.namedWindow("30-Second Chair Stand Test", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("30-Second Chair Stand Test",
                                  cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # Screen 2: test instructions — display only, no camera verification
            show_test_instructions_display_only(
                image_path="test_instructions.png")

            # Starting position wait
            self.reset_test_state()
            start_auto = False

            while not start_auto:
                ret, frame = cap.read()
                if not ret: break
                frame_count += 1
                if frame_count % frame_skip != 0: continue
                frame   = cv2.flip(frame, 1)
                results = self.pose.process(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                h, w    = frame.shape[:2]

                seated = arms_crossed = knees_visible = False
                if results.pose_landmarks:
                    lm           = results.pose_landmarks.landmark
                    seated       = self.is_user_seated(lm)
                    arms_crossed = self.are_arms_crossed(lm)
                    try:
                        lkv = lm[self.mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
                        rkv = lm[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility
                        knees_visible = lkv > 0.6 and rkv > 0.6
                    except:
                        knees_visible = False

                filled_rect(frame, 0, 0, w, 55, C_PRIMARY)
                cv2.putText(frame, "30-SECOND CHAIR STAND TEST",
                            (20, 38), FH, 1.0, C_WHITE, 2)
                cv2.putText(frame,
                            "Measures leg strength only. Use a stable chair.",
                            (20, 72), FB, 0.6, C_MUTED, 1)
                cv2.putText(frame, "Get into starting position:",
                            (20, 105), FH, 0.8, C_TEXT, 1)

                yc = 128
                if not seated:
                    status_chip(frame, 20, yc,
                                "Please sit properly on the chair", False)
                    yc += 42
                if seated and not arms_crossed:
                    status_chip(frame, 20, yc,
                                "Please cross your arms on your chest", False)
                    yc += 42
                if seated and not knees_visible:
                    status_chip(frame, 20, yc,
                                "Ensure knees are visible to the camera", False)
                    yc += 42
                if seated and arms_crossed and knees_visible:
                    filled_rect(frame, 0, h-50, w, h, C_SECONDARY)
                    cv2.putText(frame,
                                "Good position! Starting countdown...",
                                (20, h-16), FH, 0.9, C_WHITE, 2)
                    start_auto = True
                    self.countdown_start = time.time()

                cv2.imshow("30-Second Chair Stand Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    self.pose.close()
                    return

            play_audible_countdown(cap, "30-Second Chair Stand Test")

            self.start_time   = time.time()
            self.test_started = True

            while self.test_started and cap.isOpened():
                ret, frame = cap.read()
                if not ret: continue
                frame   = cv2.flip(frame, 1)
                results = self.pose.process(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if not results.pose_landmarks:
                    cv2.imshow("30-Second Chair Stand Test", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                    continue

                lm   = results.pose_landmarks.landmark
                h, w = frame.shape[:2]

                lighting_bad, lighting_msg = check_lighting(frame)
                frame_count += 1
                if frame_count % 10 == 0:
                    self._multi_people, self._people_count = \
                        check_multiple_people(frame)

                arm_violation = self.check_arm_usage(lm)
                if arm_violation: self.arm_violation_count += 1
                else:             self.arm_violation_count = 0

                if self.arm_violation_count >= self.arm_violation_threshold:
                    self.test_stopped = True
                    self.test_started = False
                    result = self.evaluate_score(0, age, gender)
                    self.record_session(age, gender, 0, result, True)
                    self.print_final_report(0, age, gender, True)
                    speak('test_stopped')
                    retry = self.show_result_overlay(cap, result, "failed")
                    if retry:
                        self.reset_test_state(); break
                    else:
                        self.display_session_history()
                        self.pose.close(); cap.release()
                        cv2.destroyAllWindows(); return

                new_state = self.calculate_body_posture(lm)
                self.update_count(new_state, lm)

                elapsed_time   = time.time() - self.start_time
                remaining_time = max(0, self.test_duration - elapsed_time)

                if remaining_time <= 0:
                    self.test_started = False
                    result = self.evaluate_score(self.stand_count, age, gender)
                    self.record_session(age, gender, self.stand_count,
                                        result, False)
                    self.print_final_report(self.stand_count, age, gender, False)
                    speak('test_complete')
                    retry = self.show_result_overlay(cap, result, "completed")
                    if retry:
                        self.reset_test_state(); break
                    else:
                        self.display_session_history()
                        self.pose.close(); cap.release()
                        cv2.destroyAllWindows(); return

                filled_rect(frame, 0, 0, w, 50, C_PRIMARY)
                cv2.putText(frame, "30-Second Chair Stand Test",
                            (16, 34), FH, 0.9, C_WHITE, 2)

                filled_rect(frame, 8,  58, 148, 118, C_SURFACE, C_BORDER, 1)
                cv2.putText(frame, "REPS", (18, 76), FB, 0.5, C_MUTED, 1)
                cv2.putText(frame, str(self.stand_count),
                            (18, 112), FH, 1.3, C_PRIMARY, 2)

                filled_rect(frame, 158, 58, 298, 118, C_SURFACE, C_BORDER, 1)
                cv2.putText(frame, "TIME", (168, 76), FB, 0.5, C_MUTED, 1)
                t_col = C_ERROR if remaining_time < 10 else C_PRIMARY
                cv2.putText(frame, f"{remaining_time:.1f}s",
                            (168, 112), FH, 1.1, t_col, 2)

                if self.test_stopped:
                    cv2.putText(frame, "TEST STOPPED",
                                (8, 145), FH, 0.9, C_ERROR, 2)

                progress_bar(frame, 0, h-6, w,
                             1.0 - remaining_time/self.test_duration, h=6)

                draw_warnings(frame, lighting_bad, lighting_msg,
                              self._multi_people, self._people_count)

                cv2.imshow("30-Second Chair Stand Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

            cap.release()
            cv2.destroyAllWindows()


# ── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    counter = SitToStandCounter()
    counter.run_test()