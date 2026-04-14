"""
Generate simple WAV sound effects at runtime using only the stdlib.
No audio assets are bundled. On import, writes small WAVs to a temp
dir and provides play() helpers.

Uses winsound on Windows; on other platforms falls back to a no-op
(the UI still works, just silently).
"""
import math
import os
import struct
import sys
import tempfile
import wave


_SND_DIR = os.path.join(tempfile.gettempdir(), "nmlf_sounds")
os.makedirs(_SND_DIR, exist_ok=True)

_SAMPLE_RATE = 44100


def _write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_SAMPLE_RATE)
        frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
        w.writeframes(frames)


def _tone(freq, duration, volume=0.4, attack=0.01, release=0.05, sweep_to=None):
    n = int(_SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        if sweep_to is not None:
            f = freq + (sweep_to - freq) * (i / n)
        else:
            f = freq
        # simple envelope
        env = 1.0
        if t < attack:
            env = t / attack
        elif t > duration - release:
            env = max(0.0, (duration - t) / release)
        out.append(volume * env * math.sin(2 * math.pi * f * t))
    return out


def _noise(duration, volume=0.3, hp=0.0):
    import random
    n = int(_SAMPLE_RATE * duration)
    out = []
    prev = 0.0
    for _ in range(n):
        s = (random.random() * 2 - 1)
        # crude high-pass
        s = s - prev * hp
        prev = s
        out.append(volume * s)
    return out


def _build_sounds():
    # tick for bit flips / reel ticks
    _write_wav(os.path.join(_SND_DIR, "tick.wav"),
               _tone(1400, 0.03, volume=0.35, attack=0.001, release=0.02))
    # soft click
    _write_wav(os.path.join(_SND_DIR, "click.wav"),
               _tone(900, 0.04, volume=0.3, attack=0.001, release=0.03))
    # case open whoosh
    whoosh = _noise(0.45, volume=0.35, hp=0.97)
    _write_wav(os.path.join(_SND_DIR, "whoosh.wav"), whoosh)
    # reveal chime (two-tone)
    chime = _tone(660, 0.15, volume=0.35) + _tone(990, 0.25, volume=0.4)
    _write_wav(os.path.join(_SND_DIR, "reveal.wav"), chime)
    # rare reveal (gold): triumphant
    rare = (_tone(523, 0.12, volume=0.35) +
            _tone(659, 0.12, volume=0.35) +
            _tone(784, 0.18, volume=0.4) +
            _tone(1046, 0.30, volume=0.45))
    _write_wav(os.path.join(_SND_DIR, "rare.wav"), rare)
    # measurement collapse (qubit)
    collapse = _tone(1200, 0.25, volume=0.35, sweep_to=300)
    _write_wav(os.path.join(_SND_DIR, "collapse.wav"), collapse)


_build_sounds()


def _path(name):
    return os.path.join(_SND_DIR, name + ".wav")


if sys.platform.startswith("win"):
    import winsound

    def play(name):
        try:
            winsound.PlaySound(_path(name), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass
else:
    def play(name):  # best-effort no-op on non-Windows
        # Try aplay if available, entirely optional
        try:
            import subprocess
            subprocess.Popen(
                ["aplay", "-q", _path(name)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
