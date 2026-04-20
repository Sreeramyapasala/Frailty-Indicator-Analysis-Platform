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

def play_audio_nonblocking(key):
    """Start playing audio without blocking. Returns True if started."""
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
    """
    Show frame, wait until audio finishes OR user presses any key.
    Returns True if skipped by keypress, False if audio finished naturally.
    Does NOT use pygame.event.get() to avoid video system error.
    """
    start = time.time()
    while time.time() - start < timeout:
        cv2.imshow(win, frame)
        k = cv2.waitKey(50)
        if k != -1:
            pygame.mixer.music.stop()
            return True  # skipped
        if not pygame.mixer.music.get_busy():
            return False  # audio finished naturally
    pygame.mixer.music.stop()
    return False

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

def speak(key):
    """Play an MP3 by key. Blocks until finished. Silently skips if missing."""
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
# SCREEN 1 — BASIC INSTRUCTIONS
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

    img = cv2.resize(img, (1280, 720))

    # show image first, then play intro
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

        # brief pause between instructions only if not skipped
        if not skipped:
            deadline = time.time() + 0.8
            while time.time() < deadline:
                cv2.imshow(WIN, display)
                if cv2.waitKey(50) != -1:
                    break

    # final screen
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
# POSE CHECK FUNCTIONS
# ─────────────────────────────────────────────────────────────────
mp_pose_global = mp.solutions.pose


def check_full_body(landmarks):
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
    visible = sum(1 for kp in key_points
                  if landmarks[kp.value].visibility > 0.4)
    if visible >= len(key_points) - 2:
        return True, "Full body detected"
    return False, "Step back so full body is visible in camera"


def _check_seated(landmarks):
    lh = landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value].y
    rh = landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value].y
    lk = landmarks[mp_pose_global.PoseLandmark.LEFT_KNEE.value].y
    rk = landmarks[mp_pose_global.PoseLandmark.RIGHT_KNEE.value].y
    hip_y  = (lh+rh)/2
    knee_y = (lk+rk)/2
    if knee_y > hip_y+0.02 and abs(hip_y-knee_y) < 0.20:
        return True, "Good — sitting position detected"
    return False, "Please sit on the front edge of the chair"


def _check_feet_flat(landmarks):
    Y_TOL = 0.07
    def flat(heel, toe):
        return abs(landmarks[heel.value].y - landmarks[toe.value].y) < Y_TOL
    L = flat(mp_pose_global.PoseLandmark.LEFT_HEEL,
             mp_pose_global.PoseLandmark.LEFT_FOOT_INDEX)
    R = flat(mp_pose_global.PoseLandmark.RIGHT_HEEL,
             mp_pose_global.PoseLandmark.RIGHT_FOOT_INDEX)
    if L and R: return True, "Good — both feet flat on the floor"
    if L or R:  return True, "Good — at least one foot flat on the floor"
    return False, "Please place both feet flat on the floor, shoulder-width apart"


def _check_arms_crossed(landmarks):
    try:
        ls = landmarks[mp_pose_global.PoseLandmark.LEFT_SHOULDER.value]
        rs = landmarks[mp_pose_global.PoseLandmark.RIGHT_SHOULDER.value]
        lw = landmarks[mp_pose_global.PoseLandmark.LEFT_WRIST.value]
        rw = landmarks[mp_pose_global.PoseLandmark.RIGHT_WRIST.value]
        sw = abs(ls.x - rs.x)
        if (math.sqrt((lw.x-rs.x)**2+(lw.y-rs.y)**2) < sw*1.2 and
                math.sqrt((rw.x-ls.x)**2+(rw.y-ls.y)**2) < sw*1.2):
            return True, "Good — arms crossed correctly"
        return False, "Please cross both arms firmly over your chest"
    except:
        return False, "Please cross both arms firmly over your chest"


def _calc_angle(a, b, c):
    ba = (a.x-b.x, a.y-b.y, a.z-b.z)
    bc = (c.x-b.x, c.y-b.y, c.z-b.z)
    dot = sum(ba[i]*bc[i] for i in range(3))
    mag = math.sqrt(sum(x**2 for x in ba))*math.sqrt(sum(x**2 for x in bc))
    if mag == 0: return 0
    return math.degrees(math.acos(max(min(dot/mag, 1.0), -1.0)))


def _check_full_stand(landmarks):
    lh = landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value]
    lk = landmarks[mp_pose_global.PoseLandmark.LEFT_KNEE.value]
    la = landmarks[mp_pose_global.PoseLandmark.LEFT_ANKLE.value]
    rh = landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value]
    rk = landmarks[mp_pose_global.PoseLandmark.RIGHT_KNEE.value]
    ra = landmarks[mp_pose_global.PoseLandmark.RIGHT_ANKLE.value]
    sh_y  = (landmarks[mp_pose_global.PoseLandmark.LEFT_SHOULDER.value].y +
             landmarks[mp_pose_global.PoseLandmark.RIGHT_SHOULDER.value].y)/2
    hip_y = (lh.y+rh.y)/2
    kn_y  = (lk.y+rk.y)/2
    torso = abs(sh_y - hip_y)
    if ((_calc_angle(lh,lk,la) > 155 or _calc_angle(rh,rk,ra) > 155) and
            hip_y < kn_y - torso*0.25):
        return True, "Good — fully upright position"
    return False, "Stand up FULLY — hips and knees straight"


def _check_no_arm_push(landmarks):
    lw = landmarks[mp_pose_global.PoseLandmark.LEFT_WRIST.value]
    rw = landmarks[mp_pose_global.PoseLandmark.RIGHT_WRIST.value]
    lh = landmarks[mp_pose_global.PoseLandmark.LEFT_HIP.value]
    rh = landmarks[mp_pose_global.PoseLandmark.RIGHT_HIP.value]
    ls = landmarks[mp_pose_global.PoseLandmark.LEFT_SHOULDER.value]
    rs = landmarks[mp_pose_global.PoseLandmark.RIGHT_SHOULDER.value]
    sw = abs(ls.x - rs.x)
    if (math.sqrt((lw.x-rs.x)**2+(lw.y-rs.y)**2) > sw*1.8 or
            math.sqrt((rw.x-ls.x)**2+(rw.y-ls.y)**2) > sw*1.8 or
            lw.y > lh.y or rw.y > rh.y):
        return False, "Keep arms crossed — do NOT push off with hands"
    return True, "Good — arms staying crossed on chest"


def _no_check(landmarks):
    return True, ""


# ── Slide definitions ─────────────────────────────────────────────
TEST_SLIDES = [
    ("Step 1 of 7 — Starting position",
     "Sit at the FRONT EDGE of the chair.\nBack straight. Feet flat on the floor.",
     "Sit at the front edge of the chair with your back straight and feet flat on the floor.",
     _check_seated, 2.0),
    ("Step 2 of 7 — Foot placement",
     "Keep your feet SHOULDER-WIDTH apart.\nDo NOT move or reposition them during the test.",
     "Keep your feet shoulder-width apart and do not move or reposition them during the test.",
     _check_feet_flat, 2.0),
    ("Step 3 of 7 — Arms position",
     "Cross your arms OVER YOUR CHEST.\nKeep them there throughout the entire test.",
     "Cross your arms over your chest and keep them there throughout the test.",
     _check_arms_crossed, 2.0),
    ("Step 4 of 7 — How to stand",
     "Stand up FULLY until hips and knees are straight.\nThen sit back down in a controlled way.",
     "Stand up fully until your hips and knees are straight, then sit back down in a controlled way.",
     _check_full_stand, 2.0),
    ("Step 5 of 7 — What counts as a rep",
     "Each rep = full SIT  ->  STAND  ->  SIT.\nBoth phases must be complete to count.",
     "Each repetition must be a full sit, stand, sit, to be counted correctly.",
     _no_check, 3.0),
    ("Step 6 of 7 — Do NOT use your arms",
     "Do NOT use your hands or arms to push off.\nThe test will STOP AUTOMATICALLY if you do.",
     "Do not use your hands or arms to push off, or the test will stop automatically.",
     _check_no_arm_push, 2.0),
    ("Step 7 of 7 — Timer",
     "Follow the on-screen timer.\nContinue until the 30-second test is complete.",
     "Follow the on-screen timer and continue until the 30-second test is complete.",
     _no_check, 3.0),
]


# ─────────────────────────────────────────────────────────────────
# SLIDE DRAW — uses pre-loaded cached image, no disk IO
# ─────────────────────────────────────────────────────────────────
def _draw_slide(frame, header, body, status_msg, status_ok,
                held, hold_needed, slide_idx, total_slides, cached_img):
    h, w = frame.shape[:2]
    half = w // 2

    # scale font sizes relative to frame height so it fits any resolution
    fs_header  = max(0.4, h / 900)
    fs_body    = max(0.4, h / 950)
    fs_small   = max(0.3, h / 1200)
    hdr_h      = max(40, int(h * 0.07))   # header bar height
    panel_h    = max(180, int(h * 0.32))  # bottom panel height
    panel_y    = h - panel_h

    # ── left white background ─────────────────────────────────────
    filled_rect(frame, 0, 0, half, h, C_BG)

    # ── paste cached image ────────────────────────────────────────
    if cached_img is not None:
        img_area_h = panel_y
        resized = cv2.resize(cached_img, (half, img_area_h))
        frame[0:img_area_h, 0:half] = resized

    # ── left header bar ───────────────────────────────────────────
    filled_rect(frame, 0, 0, half, hdr_h, C_PRIMARY)
    # split header into two lines if too long
    hdr_parts = header.split(" — ")
    if len(hdr_parts) == 2:
        cv2.putText(frame, hdr_parts[0],
                    (10, int(hdr_h * 0.5)), FH, fs_small, C_WHITE, 1)
        cv2.putText(frame, hdr_parts[1],
                    (10, int(hdr_h * 0.88)), FB, fs_small, (200,240,200), 1)
    else:
        cv2.putText(frame, header,
                    (10, int(hdr_h * 0.7)), FH, fs_small, C_WHITE, 1)

    # ── bottom panel ──────────────────────────────────────────────
    filled_rect(frame, 0, panel_y, half, h, C_SURFACE, C_BORDER, 1)
    cv2.line(frame, (0, panel_y), (half, panel_y), C_PRIMARY, 2)

    ty = panel_y + int(panel_h * 0.13)
    for ln in body.split("\n"):
        # truncate text to fit within left panel width
        max_w = half - 20
        while cv2.getTextSize(ln, FH, fs_body, 1)[0][0] > max_w and len(ln) > 5:
            ln = ln[:-1]
        cv2.putText(frame, ln, (10, ty), FH, fs_body, C_TEXT, 1)
        ty += int(panel_h * 0.16)

    ty += 4
    if status_msg:
        status_chip(frame, 10, ty, status_msg, status_ok)

    bar_y = h - int(panel_h * 0.18)
    cv2.putText(frame, "Hold position to confirm:",
                (10, bar_y - 10), FB, fs_small, C_MUTED, 1)
    progress_bar(frame, 10, bar_y, half - 10,
                 held / hold_needed if hold_needed > 0 else 0, h=12)

    cv2.putText(frame, "SPACE = skip  |  Q = quit",
                (10, h - 6), FB, fs_small * 0.85, C_MUTED, 1)

    # ── right panel header ────────────────────────────────────────
    filled_rect(frame, half, 0, w, hdr_h, C_PRIMARY)
    cv2.putText(frame, "Live Camera",
                (half + 10, int(hdr_h * 0.5)), FH, fs_small, C_WHITE, 1)
    cv2.putText(frame, "get into position",
                (half + 10, int(hdr_h * 0.88)), FB, fs_small, (200,240,200), 1)

    # ── divider line between left and right ───────────────────────
    cv2.line(frame, (half, 0), (half, h), C_PRIMARY, 2)

    # ── step dots bottom right ────────────────────────────────────
    dot_y = h - 12
    sp    = max(18, int(w * 0.018))
    sx    = half + (half - total_slides * sp) // 2
    for i in range(total_slides):
        col = C_SECONDARY if i < slide_idx else \
              C_PRIMARY   if i == slide_idx else C_BORDER
        r   = 8 if i == slide_idx else 5
        cv2.circle(frame, (sx + i * sp, dot_y), r, col, -1)
        if i == slide_idx:
            cv2.circle(frame, (sx + i * sp, dot_y), r, C_WHITE, 1)

    return frame


# ─────────────────────────────────────────────────────────────────
# SCREEN 2 — TEST INSTRUCTIONS + LIVE CAMERA CHECK
# ─────────────────────────────────────────────────────────────────
def show_test_instructions(cap, pose, image_path="test_instructions.png"):
    WIN = "30-Second Chair Stand Test"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    total = len(TEST_SLIDES)

    # ── Get frame size from camera ────────────────────────────────
    ret_t, test_f = cap.read()
    h_f    = test_f.shape[0] if ret_t else 480
    w_f    = test_f.shape[1] if ret_t else 640
    half_f = w_f // 2
    # panel_y mirrors _draw_slide logic
    panel_h_f  = max(180, int(h_f * 0.32))
    panel_y_f  = h_f - panel_h_f

    # ── Load and resize instruction image ONCE ────────────────────
    cached_img = None
    raw = cv2.imread(os.path.join(os.getcwd(), image_path))
    if raw is not None:
        cached_img = cv2.resize(raw, (half_f, panel_y_f))
        print(f"[Info] Instruction image loaded: {half_f}x{panel_y_f}")
    else:
        print(f"[Info] {image_path} not found — no image on left panel.")

    # ── Pose skip counter + cached result ────────────────────────
    POSE_SKIP   = 2
    tick        = 0
    last_ok     = False
    last_msg    = "No body detected — step into camera view"

    # play intro ONCE before any slides begin
    speak('test_intro')

    for idx, (header, body, spoken, check_fn, hold_needed) in \
            enumerate(TEST_SLIDES):

        speak(f'test_{idx+1}')

        hold_start = None
        slide_done = False

        while not slide_done:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)

            # pose detection every POSE_SKIP frames only
            tick += 1
            if tick % POSE_SKIP == 0:
                rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)
                if results.pose_landmarks:
                    last_ok, last_msg = check_fn(
                        results.pose_landmarks.landmark)
                else:
                    last_ok  = False
                    last_msg = "No body detected — step into camera view"

            # hold timer
            if last_ok:
                if hold_start is None:
                    hold_start = time.time()
                held = time.time() - hold_start
                if held >= hold_needed:
                    slide_done = True
            else:
                hold_start = None
                held = 0.0

            frame = _draw_slide(
                frame, header, body, last_msg, last_ok,
                held if hold_start else 0.0,
                hold_needed, idx, total, cached_img
            )

            cv2.imshow(WIN, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                return False
            if key == ord(' '):
                speak("Step skipped.")
                slide_done = True

        # brief pause between slides — no audio here
        time.sleep(0.3)

    # ALL slides done — say confirmed only once at the very end
    speak('test_confirmed')
    speak("All steps confirmed. Get ready to start the test.")
    time.sleep(0.5)
    return True


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
        badge(f"! {people_count} people in frame — ask others to step out",
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

            # dim background
            overlay = frame.copy()
            cv2.rectangle(overlay, (0,0), (w,h), (10,10,10), -1)
            cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

            # card dimensions — use most of the screen
            cx  = int(w * 0.08)
            cy  = int(h * 0.05)
            cw  = int(w * 0.84)
            ch  = int(h * 0.90)
            cx2 = cx + cw
            cy2 = cy + ch

            filled_rect(frame, cx, cy, cx2, cy2, C_BG, C_BORDER, 2)

            # header
            hdr_h = int(ch * 0.12)
            hdr_col = C_PRIMARY if test_status == "completed" else C_ERROR
            filled_rect(frame, cx, cy, cx2, cy + hdr_h, hdr_col)
            title = "TEST COMPLETE" if test_status == "completed" else "TEST STOPPED"
            ts = cv2.getTextSize(title, FH, 1.4, 2)[0]
            cv2.putText(frame, title,
                        (cx + (cw - ts[0])//2, cy + hdr_h - 14),
                        FH, 1.4, C_WHITE, 2)

            # helper: draw text clipped to card, auto font scale
            def card_text(text, y, font, scale, color, thickness=1):
                # shrink scale until text fits card width with padding
                pad = 24
                max_w = cw - pad * 2
                s = scale
                while cv2.getTextSize(text, font, s, thickness)[0][0] > max_w \
                        and s > 0.35:
                    s -= 0.05
                cv2.putText(frame, text, (cx + pad, y), font, s, color, thickness)
                return int(cv2.getTextSize(text, font, s, thickness)[0][1] * 1.6)

            ty = cy + hdr_h + 28

            # total stands
            line_h = card_text(f"Total Stands:  {self.stand_count}",
                                ty, FH, 1.0, C_TEXT, 2)
            ty += line_h + 10

            # divider
            cv2.line(frame, (cx+16, ty), (cx2-16, ty), C_BORDER, 1)
            ty += 18

            # assessment — may need wrapping
            assess = final_result.get('assessment', 'N/A')
            # calculate max chars that fit
            test_w = cv2.getTextSize("W" * 40, FB, 0.72, 1)[0][0]
            max_c  = int(40 * (cw - 48) / max(test_w, 1))
            for ln in wrap_text(assess, max(20, max_c)):
                lh2 = card_text(ln, ty, FB, 0.72, C_TEXT)
                ty += lh2

            ty += 6
            # disclaimer
            disc = "This test measures leg strength only and is not a diagnosis."
            card_text(disc, ty, FB, 0.58, C_MUTED)
            ty += 28

            # divider
            cv2.line(frame, (cx+16, ty), (cx2-16, ty), C_BORDER, 1)
            ty += 16

            # session info — split into two lines to avoid overflow
            if self.session_history:
                s = self.session_history[-1]
                line1 = (f"Session {len(self.session_history)}  |  "
                         f"Age: {s['age']}  |  Gender: {s['gender']}")
                line2 = (f"Count: {s['count']}  |  "
                         f"Arm violation: {'YES' if s['arm_violation'] else 'NO'}")
                card_text(line1, ty, FB, 0.58, C_MUTED)
                ty += 26
                card_text(line2, ty, FB, 0.58, C_MUTED)
                ty += 30

            # buttons — always at bottom of card with padding
            btn_y  = cy2 - 68
            btn_w  = (cw - 48) // 2
            primary_button(frame,
                           cx+16,        btn_y,
                           cx+16+btn_w,  btn_y + 52,
                           "R  -  Retry", 0.75)
            secondary_button(frame,
                             cx+32+btn_w, btn_y,
                             cx2-16,      btn_y + 52,
                             "Q  -  Quit",  0.75)

            cv2.imshow("30-Second Chair Stand Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('r'), ord('R')): return True
            if key in (ord('q'), ord('Q')): return False

    # ─────────────────────────────────────────────────────────────
    # RUN TEST
    # ─────────────────────────────────────────────────────────────
    def run_test(self):
        """Main function to run the 30-second chair stand test."""

        age, gender = self.get_patient_info()

        # Screen 1: basic instructions — no camera needed
        show_basic_instructions(image_path="basic_instructions.png")

        while True:  # retry loop

            frame_skip  = 2
            frame_count = 0

            # Auto-select camera
            for i in range(5):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    print(f"Camera found at index {i}")
                    break
                cap.release()
            else:
                print("No camera found in indices 0-4")
                return

            # 640x480 — smooth real-time performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cv2.namedWindow("30-Second Chair Stand Test", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("30-Second Chair Stand Test",
                                  cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # Screen 2: test instructions + live camera checks
            all_passed = show_test_instructions(
                cap, self.pose, image_path="test_instructions.png")
            if not all_passed:
                cap.release()
                cv2.destroyAllWindows()
                self.pose.close()
                return

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

            # Countdown
            play_audible_countdown(cap, "30-Second Chair Stand Test")

            # Main 30-second test loop
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

                # edge case 1: lighting (every frame — very cheap)
                lighting_bad, lighting_msg = check_lighting(frame)

                # edge case 2: multiple people (every 10 frames — expensive)
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
                    result = self.evaluate_score(
                        self.stand_count, age, gender)
                    self.record_session(age, gender, self.stand_count,
                                        result, False)
                    self.print_final_report(
                        self.stand_count, age, gender, False)
                    speak('test_complete')
                    retry = self.show_result_overlay(
                        cap, result, "completed")
                    if retry:
                        self.reset_test_state(); break
                    else:
                        self.display_session_history()
                        self.pose.close(); cap.release()
                        cv2.destroyAllWindows(); return

                # HUD
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