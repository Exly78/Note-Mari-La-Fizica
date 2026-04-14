# Note Mari La Fizica

A small desktop teaching app written in Python + Tkinter. Two tabs:

1. **Bits & Qubits** - interactive explanation of how classical bits
   and quantum bits differ, with a live 4-bit register, a binary auto-
   counter, and a 3-qubit superposition playground with a measurement
   button and a joint-probability bar chart.
2. **Probability / Case Simulator** - a CS2-style case opening
   simulator built around the Kilowatt Case item pool. Each rarity
   (Mil-Spec, Restricted, Classified, Covert, and the rare Special
   Item tier) has its own weight slider. Totals above 100% are auto-
   moderated before the roll so nothing breaks. The Open Case button
   plays a horizontal reel animation with ticking and reveal sound
   effects.

## Running from source

```
python -m pip install -r requirements.txt
python main.py
```

Python 3.10 or newer is recommended. Tkinter ships with Python on
Windows and macOS; on Linux install `python3-tk`.

## Building a standalone Windows `.exe`

```
build.bat
```

This installs PyInstaller and produces `dist\NoteMariLaFizica.exe`, a
single-file executable you can double-click. Use `build.sh` on
macOS/Linux for the equivalent binary.

## How the two simulators work (short version)

### Bits

A bit is either 0 or 1. A register of `N` bits stores exactly one
`N`-bit number. The tab lets you toggle each bit and auto-increment
the whole register through `0000 -> 0001 -> 0010 -> ... -> 1111`.

### Qubits

A qubit is a superposition `a|0> + b|1>` where `|a|^2 + |b|^2 = 1`.
A register of `N` qubits holds every one of the `2^N` basis states at
once, each with a probability given by the product of the chosen
amplitudes. The tab visualises these joint probabilities as a bar
chart. Press **Measure** and the superposition collapses to exactly
one basis state (weighted by probability), sliding each qubit hard to
0 or 1. That collapse is the single most important difference between
a classical bit and a qubit.

### Probability simulator

- Sliders assign a raw weight (in percent) to each rarity.
- The raw total is always shown live.
- Before any roll the weights are normalised so they sum to 1.0,
  regardless of whether the user's raw total was over, under, or
  exactly 100%. This is the "automatic moderation" described in the
  task - it keeps the simulation well-defined no matter what the user
  types into the sliders.
- A random number in `[0, 1)` is drawn, the rarity tier whose
  cumulative range contains it is selected, and a specific item is
  picked uniformly at random from that tier's pool.
- The reel animation is decorative: the winner is decided the instant
  you click Open Case.

## About item art

The item pool is modeled after the in-game CS2 Kilowatt Case. Only
item **names** are referenced in this project. Item visuals displayed
in the reel are procedurally generated stylised placeholder cards
(rarity-coloured gradients, simple weapon silhouettes drawn with PIL
primitives, and the item name). No copyrighted game art or audio is
bundled or downloaded by this application.

## Project layout

```
main.py                   entry point
app/__init__.py
app/theme.py              shared colors + ttk styling
app/sounds.py             procedurally generated WAV sound effects
app/item_art.py           PIL-based procedural item-card renderer
app/case_data.py          rarity tiers, default weights, item pool
app/bits_tab.py           tab 1: bits & qubits
app/case_tab.py           tab 2: probability / case simulator
requirements.txt
build.bat / build.sh      packaging scripts
```
