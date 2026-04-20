import pyttsx3
import cv2
import os

# ── Test 1: pyttsx3 basic ────────────────────────────────────────
print("Testing pyttsx3...")
engine = pyttsx3.init()
voices = engine.getProperty('voices')
print(f"Available voices: {len(voices)}")
for i, v in enumerate(voices):
    print(f"  [{i}] {v.id}")

engine.setProperty('rate', 145)
engine.setProperty('volume', 1.0)
engine.say("Hello. This is a test of the audio system. Can you hear me?")
engine.runAndWait()
print("pyttsx3 test done.")

# ── Test 2: image loading ────────────────────────────────────────
print("\nTesting image loading...")
cwd = os.getcwd()
print(f"Current working directory: {cwd}")
print("Files in directory:")
for f in os.listdir(cwd):
    print(f"  {f}")

for name in ["basic_instructions.png", "test_instructions.png"]:
    path = os.path.join(cwd, name)
    img = cv2.imread(path)
    if img is None:
        print(f"  FAIL: {name} not found at {path}")
    else:
        print(f"  OK:   {name} loaded — size {img.shape[1]}x{img.shape[0]}")