"""
Case loot pool definition.

Item pool models the structure of the CS2 Kilowatt Case: a set of
weapon+skin names grouped by rarity tier (Mil-Spec/Blue, Restricted/
Purple, Classified/Pink, Covert/Red, Rare Special / Gold knives).

Notes:
- Only item *names* and category metadata are stored here - no image
  or audio assets from the game are bundled or distributed with this
  project. Item visuals in the simulator are generated procedurally
  at runtime as stylised placeholder cards (weapon silhouette + rarity
  border + name), which is what the application displays.
- Weights inside a rarity tier are uniform by default; the user-set
  percentage applies to the rarity tier itself. Within a tier the
  specific item is picked uniformly at random.
"""

# Rarity keys used everywhere in the app
RARITIES = ["blue", "purple", "pink", "red", "gold"]

RARITY_LABEL = {
    "blue":   "Mil-Spec (Blue)",
    "purple": "Restricted (Purple)",
    "pink":   "Classified (Pink)",
    "red":    "Covert (Red)",
    "gold":   "Rare Special Item (Gold)",
}

# Realistic in-game drop percentages, provided here as the DEFAULT
# starting weights. They sum to 100% but the user can edit them.
DEFAULT_WEIGHTS = {
    "blue":   79.92,
    "purple": 15.98,
    "pink":    3.20,
    "red":     0.64,
    "gold":    0.26,
}


# Item pool modeled after the Kilowatt Case (CS2).
# Each entry: (weapon, skin_name)
CASE_NAME = "Kilowatt Case"

ITEMS = {
    "blue": [
        ("Dual Berettas", "Hideout"),
        ("MAG-7",         "Insomnia"),
        ("MP7",           "Just Smile"),
        ("Sawed-Off",     "Analog Input"),
        ("SG 553",        "Cyberforce"),
        ("USP-S",         "Jawbreaker"),
        ("M4A1-S",        "Black Lotus"),
    ],
    "purple": [
        ("AUG",    "Smoke Jumper"),
        ("Nova",   "Dark Sigil"),
        ("Tec-9",  "Slag"),
        ("XM1014", "Irezumi"),
        ("M4A4",   "Etched Sigil"),
    ],
    "pink": [
        ("AK-47",     "Inheritance"),
        ("Glock-18",  "Block-18"),
        ("Zeus x27",  "Olympus Mons"),
    ],
    "red": [
        ("AWP",  "Chrome Cannon"),
        ("Desert Eagle", "Mecha Industries"),
    ],
    "gold": [
        ("Kukri Knife",   "Fade"),
        ("Kukri Knife",   "Slaughter"),
        ("Kukri Knife",   "Crimson Web"),
        ("Kukri Knife",   "Tiger Tooth"),
        ("Kukri Knife",   "Doppler"),
        ("Kukri Knife",   "Marble Fade"),
    ],
}
