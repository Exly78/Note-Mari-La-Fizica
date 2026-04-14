"""
Probability / Case opening simulator tab.

Features:
- 5 rarity sliders (blue, purple, pink, red, gold) that give a
  percent chance to each tier.
- Live "Total" readout; if the total exceeds 100% the values are
  automatically moderated (softmax-style rescale) before a roll so
  nothing breaks.
- "Open Case" button: plays a horizontal reel animation across all
  items in the pool (weighted by the moderated probabilities), with
  ticking sound effects and a reveal chime on land.
- Rare tier lands play a special triumphant sound.
- Explanation panel at the bottom describing how the probability
  moderation works.
"""
import random
import tkinter as tk
from tkinter import ttk

from .theme import COLORS
from . import sounds
from . import item_art
from .case_data import (
    RARITIES, RARITY_LABEL, DEFAULT_WEIGHTS, ITEMS, CASE_NAME,
)


CARD_W = 200
CARD_H = 138
CARD_GAP = 12


PROBABILITY_EXPLANATION = (
    "How the probability works:\n"
    "- Every rarity (Mil-Spec, Restricted, Classified, Covert, and the "
    "rare Special Item) gets a percentage of the total drop chance, set "
    "by the sliders above.\n"
    "- The simulator shows a live total. If you set values that sum to "
    "more than 100%, nothing breaks: the simulator automatically "
    "moderates them by rescaling the whole set down to 100% (each weight "
    "keeps its relative share). If the total is below 100%, the "
    "'leftover' is distributed proportionally so the opened case always "
    "drops something.\n"
    "- When you press Open Case, a random value in [0, 1) is rolled. "
    "The rarity tier whose cumulative range contains that roll is "
    "selected. Then a specific item is picked uniformly at random from "
    "that tier's pool.\n"
    "- The on-screen reel is just an animation - the final item is "
    "decided by the random roll, not by the reel's movement. This "
    "mirrors how real case openings show an animation to make the "
    "instant decision feel dramatic."
)


class CaseTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="TFrame")

        # Scrollable container
        outer = ttk.Frame(self, style="TFrame")
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = ttk.Frame(canvas, style="TFrame")
        win = canvas.create_window((0, 0), window=content, anchor="nw")

        def _resize(_e=None):
            canvas.itemconfig(win, width=canvas.winfo_width())
            canvas.configure(scrollregion=canvas.bbox("all"))
        content.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)

        # state
        self._weights = {r: tk.DoubleVar(value=DEFAULT_WEIGHTS[r]) for r in RARITIES}
        self._moderated_label = None
        self._anim_job = None
        self._image_cache = {}  # (weapon, skin, rarity) -> PhotoImage

        self._build_header(content)
        self._build_weights(content)
        self._build_reel(content)
        self._build_explanation(content)

        self._refresh_totals()

    # -------------------------------------------------- HEADER
    def _build_header(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=(20, 10))

        ttk.Label(wrap, text=f"{CASE_NAME} - Probability Simulator",
                  style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text=("Assign weights to each rarity tier below. Totals above "
                  "100% are auto-moderated. Press Open Case to watch a "
                  "case roll against your weights."),
            style="Panel.TLabel",
            wraplength=1020, justify="left",
        ).pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------- WEIGHTS
    def _build_weights(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=8)

        for i, r in enumerate(RARITIES):
            row = ttk.Frame(wrap, style="Panel.TFrame")
            row.pack(fill="x", pady=4)

            swatch = tk.Canvas(row, width=22, height=22,
                               bg=COLORS["panel"], highlightthickness=0)
            swatch.create_rectangle(1, 1, 21, 21,
                                    fill=COLORS[r], outline=COLORS["border"])
            swatch.pack(side="left", padx=(0, 10))

            ttk.Label(row, text=RARITY_LABEL[r], style="Panel.TLabel",
                      width=26, anchor="w").pack(side="left")

            scale = ttk.Scale(
                row, from_=0, to=100, orient="horizontal",
                variable=self._weights[r], length=360,
                command=lambda _e: self._refresh_totals(),
            )
            scale.pack(side="left", padx=10)

            val_lbl = ttk.Label(row, text="", style="Panel.TLabel",
                                font=("Consolas", 10, "bold"), width=10)
            val_lbl.pack(side="left")
            self._weights[r].trace_add(
                "write", lambda *_a, lbl=val_lbl, rr=r: lbl.configure(
                    text=f"{self._weights[rr].get():5.2f}%"
                )
            )
            val_lbl.configure(text=f"{self._weights[r].get():5.2f}%")

            mod_lbl = ttk.Label(row, text="", style="Dim.TLabel", width=22)
            mod_lbl.pack(side="left", padx=(16, 0))
            setattr(self, f"_mod_lbl_{r}", mod_lbl)

        # totals row
        footer = ttk.Frame(wrap, style="Panel.TFrame")
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, text="Raw total:", style="Dim.TLabel").pack(side="left")
        self._total_var = tk.StringVar(value="0.00%")
        ttk.Label(footer, textvariable=self._total_var, style="Panel.TLabel",
                  font=("Consolas", 11, "bold")).pack(side="left", padx=(6, 18))
        self._mod_status_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self._mod_status_var, style="Dim.TLabel").pack(side="left")

        ttk.Button(footer, text="Reset to realistic", command=self._reset_weights).pack(side="right")
        ttk.Button(footer, text="Normalize now", command=self._normalize_in_place).pack(side="right", padx=6)

    def _reset_weights(self):
        for r in RARITIES:
            self._weights[r].set(DEFAULT_WEIGHTS[r])
        self._refresh_totals()

    def _normalize_in_place(self):
        mod = self._moderated_weights()
        for r in RARITIES:
            self._weights[r].set(round(mod[r] * 100, 2))
        self._refresh_totals()

    def _raw_weights(self):
        return {r: max(0.0, float(self._weights[r].get())) for r in RARITIES}

    def _moderated_weights(self):
        """Return a normalised distribution that always sums to 1.0.

        - If everything is zero, fall back to the realistic defaults.
        - Otherwise rescale proportionally. This handles both over-100
          and under-100 totals with the same operation.
        """
        raw = self._raw_weights()
        s = sum(raw.values())
        if s <= 0:
            s = sum(DEFAULT_WEIGHTS.values())
            return {r: DEFAULT_WEIGHTS[r] / s for r in RARITIES}
        return {r: raw[r] / s for r in RARITIES}

    def _refresh_totals(self):
        raw = self._raw_weights()
        total = sum(raw.values())
        self._total_var.set(f"{total:6.2f}%")

        mod = self._moderated_weights()
        for r in RARITIES:
            lbl = getattr(self, f"_mod_lbl_{r}")
            lbl.configure(text=f"~ effective {mod[r] * 100:5.2f}%")

        if abs(total - 100.0) < 0.01:
            self._mod_status_var.set("Total = 100% (no moderation needed)")
        elif total > 100.0:
            self._mod_status_var.set(
                f"Total {total:.2f}% > 100% - auto-moderated down"
            )
        else:
            self._mod_status_var.set(
                f"Total {total:.2f}% < 100% - scaled up to fill 100%"
            )

    # ---------------------------------------------------- REEL
    def _build_reel(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=8)

        ttk.Label(wrap, text="Case opening", style="PanelTitle.TLabel").pack(anchor="w")

        # reel canvas with a center marker
        self._reel_canvas = tk.Canvas(
            wrap, height=CARD_H + 40, bg=COLORS["panel2"],
            highlightthickness=1, highlightbackground=COLORS["border"],
        )
        self._reel_canvas.pack(fill="x", pady=(8, 6))
        self._reel_canvas.bind("<Configure>", lambda _e: self._draw_static_reel())

        btn_row = ttk.Frame(wrap, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(6, 0))
        self._open_btn = ttk.Button(
            btn_row, text="Open Case", style="Accent.TButton",
            command=self._open_case,
        )
        self._open_btn.pack(side="left")

        self._result_var = tk.StringVar(value="Waiting for your roll.")
        ttk.Label(btn_row, textvariable=self._result_var,
                  style="Panel.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=16)

        # reel data
        self._reel_items = self._build_reel_pool()
        self._draw_static_reel()

    def _build_reel_pool(self):
        """Flat list of (weapon, skin, rarity) for the visual reel.

        Each rarity contributes multiple copies so the reel looks
        populated even for rare tiers.
        """
        pool = []
        counts = {"blue": 6, "purple": 4, "pink": 3, "red": 2, "gold": 1}
        for r in RARITIES:
            for weapon, skin in ITEMS[r]:
                for _ in range(counts[r]):
                    pool.append((weapon, skin, r))
        random.shuffle(pool)
        return pool

    def _get_card(self, item):
        if item not in self._image_cache:
            weapon, skin, rarity = item
            pil = item_art.render_item_card(weapon, skin, rarity, (CARD_W, CARD_H))
            self._image_cache[item] = item_art.to_photo(pil)
        return self._image_cache[item]

    def _draw_static_reel(self, offset=0):
        c = self._reel_canvas
        c.delete("all")
        w = c.winfo_width() or 1100
        h = CARD_H + 40
        cx = w // 2

        # Draw enough cards around offset to fill the width.
        step = CARD_W + CARD_GAP
        n = len(self._reel_items)
        if n == 0:
            return

        # First visible card index so cards scroll from right to left.
        half = w // 2 + step
        start_px = offset - half
        start_i = int(start_px // step) - 1
        px = start_i * step - offset + cx

        i = start_i
        while px < w + step:
            idx = i % n
            img = self._get_card(self._reel_items[idx])
            c.create_image(px + CARD_W // 2, 20 + CARD_H // 2, image=img)
            px += step
            i += 1

        # center marker line
        c.create_line(cx, 0, cx, h, fill=COLORS["gold"], width=2)
        c.create_polygon([cx - 8, 0, cx + 8, 0, cx, 10],
                         fill=COLORS["gold"], outline="")
        c.create_polygon([cx - 8, h, cx + 8, h, cx, h - 10],
                         fill=COLORS["gold"], outline="")

    def _pick_item(self):
        mod = self._moderated_weights()
        r = random.random()
        acc = 0.0
        rarity = RARITIES[-1]
        for rr in RARITIES:
            acc += mod[rr]
            if r <= acc:
                rarity = rr
                break
        weapon, skin = random.choice(ITEMS[rarity])
        return (weapon, skin, rarity)

    def _open_case(self):
        if self._anim_job is not None:
            return
        self._open_btn.configure(state="disabled")
        self._result_var.set("Rolling...")
        sounds.play("whoosh")

        chosen = self._pick_item()

        # Ensure the chosen item exists in the reel list; insert it at a
        # far offset so the animation glides to it.
        n = len(self._reel_items)
        step = CARD_W + CARD_GAP
        # place the target index far to the right of current 0
        target_index = n + random.randint(n * 2, n * 3)
        # overwrite the slot at target_index % n so the landing card matches
        self._reel_items[target_index % n] = chosen

        target_offset = target_index * step
        # Ease-out animation
        self._anim_start = 0
        self._anim_target = target_offset
        self._anim_t = 0
        self._anim_duration = 60  # frames
        self._anim_rarity = chosen[2]
        self._anim_chosen = chosen
        self._tick_anim()

    def _tick_anim(self):
        t = self._anim_t / self._anim_duration
        # ease out cubic
        eased = 1 - (1 - t) ** 3
        offset = self._anim_start + (self._anim_target - self._anim_start) * eased
        self._draw_static_reel(offset=offset)

        # tick sound every few frames, less often near the end
        if self._anim_t % max(2, int(2 + t * 8)) == 0 and t < 0.98:
            sounds.play("tick")

        self._anim_t += 1
        if self._anim_t <= self._anim_duration:
            self._anim_job = self.after(28, self._tick_anim)
        else:
            self._anim_job = None
            self._finish_anim()

    def _finish_anim(self):
        weapon, skin, rarity = self._anim_chosen
        if rarity in ("red", "gold"):
            sounds.play("rare")
        else:
            sounds.play("reveal")
        self._result_var.set(
            f"You unboxed: {skin} ({weapon})  -  {RARITY_LABEL[rarity]}"
        )
        self._open_btn.configure(state="normal")

    # ---------------------------------------------- EXPLANATION
    def _build_explanation(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=(8, 20))
        ttk.Label(wrap, text="How this probability simulation works",
                  style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(wrap, text=PROBABILITY_EXPLANATION,
                  style="Panel.TLabel",
                  wraplength=1020, justify="left").pack(anchor="w", pady=(6, 0))
