"""
Bits & Qubits tab.

Top half: classical bits - a 4-bit register, toggleable, with live
binary-counter animation that shows 0000 -> 0001 -> 0010 -> 0011 ...

Bottom half: qubits - a 3-qubit register where each qubit is a
superposition (alpha|0> + beta|1>). The user can slide the |1>
probability of each qubit. A "Measure" button collapses to a basis
state, weighted by the current amplitudes. A bar graph shows the
probability of every basis state (000..111), visualising how a qubit
register holds all possible values simultaneously - the key
difference from classical bits.
"""
import math
import random
import tkinter as tk
from tkinter import ttk

from .theme import COLORS
from . import sounds


BIT_COUNT = 4
QUBIT_COUNT = 3


BITS_EXPLANATION = (
    "Classical bit: the smallest unit of information in a normal computer. "
    "A bit is always exactly one of two values - 0 or 1 - like a switch that "
    "is either off or on. A register of N bits can store one N-bit number at "
    "a time. Counting in binary means incrementing that number the same way "
    "decimal counts, but with only two digits: 0000, 0001, 0010, 0011, 0100, "
    "0101, ... Click any bit below to flip it, or press Auto-count to watch "
    "a 4-bit register tick through every value 0-15."
)

QUBITS_EXPLANATION = (
    "Quantum bit (qubit): instead of being forced to 0 or 1, a qubit lives "
    "in a superposition a|0> + b|1>, where |a|^2 and |b|^2 are the "
    "probabilities of measuring 0 or 1. Until you measure it, it is BOTH "
    "values at once - weighted by those amplitudes. A register of N qubits "
    "does not store one N-bit number; it simultaneously represents every "
    "one of the 2^N possible values, each with its own probability. When "
    "you finally measure the register, the superposition collapses to "
    "exactly one of those basis states at random, weighted by probability. "
    "Slide the |1> probability for each qubit below and watch how the 2^N "
    "joint probabilities change in the bar chart. That chart is what the "
    "qubits are 'holding' before measurement."
)

DIFFERENCE_NOTE = (
    "Main difference: 3 classical bits store exactly one of 8 values. 3 "
    "qubits hold all 8 values at once, each with its own probability, and "
    "only pick one when you measure them."
)


class BitsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="TFrame")

        # Use a plain Canvas-backed scroll area so the whole thing fits
        # on smaller screens too.
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

        # Mouse wheel scrolling
        def _wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _wheel)

        # Build the two sections
        self._build_bits_section(content)
        ttk.Separator(content, orient="horizontal").pack(fill="x", padx=20, pady=14)
        self._build_qubits_section(content)

        # state
        self._bit_values = [0] * BIT_COUNT
        self._auto_job = None
        self._refresh_bits()

        self._qubit_p1 = [0.5] * QUBIT_COUNT  # P(|1>) for each qubit
        self._refresh_qubits()

    # ------------------------------------------------------------------ BITS
    def _build_bits_section(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=(20, 10))

        ttk.Label(wrap, text="Classical Bits", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            wrap, text=BITS_EXPLANATION, style="Panel.TLabel",
            wraplength=1020, justify="left",
        ).pack(anchor="w", pady=(4, 12))

        row = ttk.Frame(wrap, style="Panel.TFrame")
        row.pack(fill="x", pady=(4, 6))

        self._bit_canvases = []
        for i in range(BIT_COUNT):
            idx = BIT_COUNT - 1 - i  # MSB on the left
            c = tk.Canvas(
                row, width=110, height=130,
                bg=COLORS["panel"], highlightthickness=0,
            )
            c.grid(row=0, column=i, padx=10)
            c.bind("<Button-1>", lambda _e, k=idx: self._toggle_bit(k))
            self._bit_canvases.append((idx, c))

        # decimal + binary readout
        info = ttk.Frame(wrap, style="Panel.TFrame")
        info.pack(fill="x", pady=(10, 6))
        self._bit_binary_var = tk.StringVar(value="0000")
        self._bit_decimal_var = tk.StringVar(value="0")
        ttk.Label(info, text="Binary:", style="Dim.TLabel").grid(row=0, column=0, padx=(0, 6))
        ttk.Label(info, textvariable=self._bit_binary_var,
                  style="Panel.TLabel",
                  font=("Consolas", 20, "bold")).grid(row=0, column=1, padx=(0, 24))
        ttk.Label(info, text="Decimal:", style="Dim.TLabel").grid(row=0, column=2, padx=(0, 6))
        ttk.Label(info, textvariable=self._bit_decimal_var,
                  style="Panel.TLabel",
                  font=("Consolas", 20, "bold")).grid(row=0, column=3)

        btns = ttk.Frame(wrap, style="Panel.TFrame")
        btns.pack(fill="x", pady=(12, 0))
        ttk.Button(btns, text="Reset", command=self._reset_bits).pack(side="left", padx=4)
        self._auto_btn = ttk.Button(btns, text="Auto-count", command=self._toggle_autocount)
        self._auto_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="+1", command=self._increment_bits).pack(side="left", padx=4)

    def _draw_bit(self, canvas, value):
        canvas.delete("all")
        w, h = 110, 130
        # card background
        canvas.create_rectangle(2, 2, w - 2, h - 2, fill=COLORS["panel2"],
                                outline=COLORS["border"], width=2)
        # big digit
        color = COLORS["good"] if value else COLORS["text_dim"]
        canvas.create_text(w // 2, h // 2 - 8, text=str(value),
                           fill=color, font=("Consolas", 46, "bold"))
        # led dot
        r = 7
        cx, cy = w // 2, h - 22
        fill = COLORS["good"] if value else "#3a3f4d"
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=fill, outline="")

    def _refresh_bits(self):
        for idx, c in self._bit_canvases:
            self._draw_bit(c, self._bit_values[idx])
        binary = "".join(str(self._bit_values[BIT_COUNT - 1 - i]) for i in range(BIT_COUNT))
        self._bit_binary_var.set(binary)
        dec = sum(self._bit_values[i] * (1 << i) for i in range(BIT_COUNT))
        self._bit_decimal_var.set(str(dec))

    def _toggle_bit(self, k):
        self._bit_values[k] ^= 1
        sounds.play("click")
        self._refresh_bits()

    def _reset_bits(self):
        if self._auto_job is not None:
            self.after_cancel(self._auto_job)
            self._auto_job = None
            self._auto_btn.configure(text="Auto-count")
        self._bit_values = [0] * BIT_COUNT
        self._refresh_bits()

    def _increment_bits(self):
        dec = sum(self._bit_values[i] * (1 << i) for i in range(BIT_COUNT))
        dec = (dec + 1) % (1 << BIT_COUNT)
        for i in range(BIT_COUNT):
            self._bit_values[i] = (dec >> i) & 1
        sounds.play("tick")
        self._refresh_bits()

    def _toggle_autocount(self):
        if self._auto_job is None:
            self._auto_btn.configure(text="Stop")
            self._tick_autocount()
        else:
            self.after_cancel(self._auto_job)
            self._auto_job = None
            self._auto_btn.configure(text="Auto-count")

    def _tick_autocount(self):
        self._increment_bits()
        self._auto_job = self.after(600, self._tick_autocount)

    # ---------------------------------------------------------------- QUBITS
    def _build_qubits_section(self, parent):
        wrap = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        wrap.pack(fill="x", padx=20, pady=(6, 20))

        ttk.Label(wrap, text="Quantum Bits (Qubits)",
                  style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            wrap, text=QUBITS_EXPLANATION, style="Panel.TLabel",
            wraplength=1020, justify="left",
        ).pack(anchor="w", pady=(4, 8))
        ttk.Label(
            wrap, text=DIFFERENCE_NOTE, style="Panel.TLabel",
            wraplength=1020, justify="left",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        body = ttk.Frame(wrap, style="Panel.TFrame")
        body.pack(fill="x")

        # Left: qubit controls
        left = ttk.Frame(body, style="Panel.TFrame")
        left.pack(side="left", fill="y", padx=(0, 24))

        self._qubit_vars = []
        self._qubit_canvases = []
        self._qubit_labels = []
        for i in range(QUBIT_COUNT):
            q_wrap = ttk.Frame(left, style="Panel.TFrame")
            q_wrap.pack(fill="x", pady=6)

            ttk.Label(q_wrap, text=f"Qubit q{i}",
                      style="Panel.TLabel",
                      font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")

            c = tk.Canvas(q_wrap, width=120, height=120,
                          bg=COLORS["panel"], highlightthickness=0)
            c.grid(row=1, column=0, rowspan=2, padx=(0, 14), pady=4)
            self._qubit_canvases.append(c)

            v = tk.DoubleVar(value=50.0)
            self._qubit_vars.append(v)
            scl = ttk.Scale(
                q_wrap, from_=0, to=100, orient="horizontal",
                variable=v, length=280,
                command=lambda _e, k=i: self._qubit_slider(k),
            )
            scl.grid(row=1, column=1, sticky="we")

            lbl = ttk.Label(q_wrap, text="P(|0>)=50%  P(|1>)=50%",
                            style="Panel.TLabel",
                            font=("Consolas", 10))
            lbl.grid(row=2, column=1, sticky="w")
            self._qubit_labels.append(lbl)

        btns = ttk.Frame(left, style="Panel.TFrame")
        btns.pack(fill="x", pady=(12, 0))
        ttk.Button(btns, text="Reset to |0>", command=self._reset_qubits).pack(side="left", padx=4)
        ttk.Button(btns, text="Hadamard all (50/50)",
                   command=self._hadamard_qubits).pack(side="left", padx=4)
        ttk.Button(btns, text="Measure",
                   style="Accent.TButton",
                   command=self._measure_qubits).pack(side="left", padx=4)

        # Right: probability chart + last measurement
        right = ttk.Frame(body, style="Panel.TFrame")
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="Joint probability of basis states |q2 q1 q0>",
                  style="Panel.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self._prob_canvas = tk.Canvas(
            right, width=520, height=260,
            bg=COLORS["panel2"], highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self._prob_canvas.pack(anchor="w", pady=(6, 8))

        self._measured_var = tk.StringVar(value="Last measurement: -")
        ttk.Label(right, textvariable=self._measured_var,
                  style="Panel.TLabel",
                  font=("Consolas", 12, "bold")).pack(anchor="w")

    def _qubit_slider(self, k):
        self._qubit_p1[k] = float(self._qubit_vars[k].get()) / 100.0
        self._refresh_qubits()

    def _reset_qubits(self):
        for i in range(QUBIT_COUNT):
            self._qubit_p1[i] = 0.0
            self._qubit_vars[i].set(0.0)
        self._refresh_qubits()

    def _hadamard_qubits(self):
        for i in range(QUBIT_COUNT):
            self._qubit_p1[i] = 0.5
            self._qubit_vars[i].set(50.0)
        self._refresh_qubits()

    def _draw_qubit_circle(self, canvas, p1):
        canvas.delete("all")
        w, h = 120, 120
        cx, cy = w // 2, h // 2
        r = 48
        # outer ring
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           outline=COLORS["border"], width=2)
        # "probability wedge" - purple wedge is P(|1>)
        deg = 360 * p1
        if deg > 0.01:
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=90, extent=-deg,
                              fill=COLORS["accent2"], outline="")
        if deg < 359.99:
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=90 - deg, extent=-(360 - deg),
                              fill=COLORS["accent"], outline="")
        # center label
        canvas.create_oval(cx - 18, cy - 18, cx + 18, cy + 18,
                           fill=COLORS["panel"], outline=COLORS["border"])
        canvas.create_text(cx, cy, text="?",
                           fill=COLORS["text"],
                           font=("Segoe UI", 14, "bold"))
        # legend
        canvas.create_rectangle(6, h - 16, 14, h - 8, fill=COLORS["accent"], outline="")
        canvas.create_text(34, h - 12, text="|0>",
                           fill=COLORS["text_dim"],
                           font=("Segoe UI", 9))
        canvas.create_rectangle(60, h - 16, 68, h - 8, fill=COLORS["accent2"], outline="")
        canvas.create_text(88, h - 12, text="|1>",
                           fill=COLORS["text_dim"],
                           font=("Segoe UI", 9))

    def _refresh_qubits(self):
        for i in range(QUBIT_COUNT):
            p1 = self._qubit_p1[i]
            p0 = 1.0 - p1
            self._draw_qubit_circle(self._qubit_canvases[i], p1)
            self._qubit_labels[i].configure(
                text=f"P(|0>)={p0 * 100:5.1f}%   P(|1>)={p1 * 100:5.1f}%"
            )
        self._draw_prob_chart()

    def _joint_probs(self):
        n = 1 << QUBIT_COUNT
        probs = []
        for state in range(n):
            p = 1.0
            for i in range(QUBIT_COUNT):
                bit = (state >> i) & 1
                p *= self._qubit_p1[i] if bit else (1.0 - self._qubit_p1[i])
            probs.append(p)
        return probs

    def _draw_prob_chart(self, highlight=None):
        c = self._prob_canvas
        c.delete("all")
        n = 1 << QUBIT_COUNT
        W = int(c.cget("width"))
        H = int(c.cget("height"))
        pad_l, pad_r, pad_t, pad_b = 44, 16, 18, 40
        plot_w = W - pad_l - pad_r
        plot_h = H - pad_t - pad_b
        # grid
        for i in range(5):
            y = pad_t + plot_h * i / 4
            c.create_line(pad_l, y, W - pad_r, y, fill=COLORS["border"])
            val = 100 - i * 25
            c.create_text(pad_l - 6, y, text=f"{val}%",
                          fill=COLORS["text_dim"],
                          anchor="e", font=("Segoe UI", 8))

        probs = self._joint_probs()
        bw = plot_w / n * 0.72
        gap = plot_w / n
        for i, p in enumerate(probs):
            x0 = pad_l + i * gap + (gap - bw) / 2
            x1 = x0 + bw
            bh = plot_h * p
            y0 = pad_t + (plot_h - bh)
            y1 = pad_t + plot_h
            fill = COLORS["accent2"] if (highlight is not None and i == highlight) else COLORS["accent"]
            c.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")
            label = "|" + format(i, f"0{QUBIT_COUNT}b") + ">"
            c.create_text((x0 + x1) / 2, pad_t + plot_h + 14,
                          text=label, fill=COLORS["text"],
                          font=("Consolas", 9, "bold"))
            c.create_text((x0 + x1) / 2, y0 - 8,
                          text=f"{p * 100:.1f}%", fill=COLORS["text_dim"],
                          font=("Segoe UI", 8))

    def _measure_qubits(self):
        probs = self._joint_probs()
        r = random.random()
        acc = 0.0
        chosen = 0
        for i, p in enumerate(probs):
            acc += p
            if r <= acc:
                chosen = i
                break
        # collapse: each qubit becomes its measured bit (slider snaps to 0 or 100)
        for i in range(QUBIT_COUNT):
            bit = (chosen >> i) & 1
            self._qubit_p1[i] = float(bit)
            self._qubit_vars[i].set(100.0 if bit else 0.0)
        sounds.play("collapse")
        for i in range(QUBIT_COUNT):
            self._draw_qubit_circle(self._qubit_canvases[i], self._qubit_p1[i])
            p1 = self._qubit_p1[i]
            self._qubit_labels[i].configure(
                text=f"P(|0>)={(1 - p1) * 100:5.1f}%   P(|1>)={p1 * 100:5.1f}%"
            )
        self._draw_prob_chart(highlight=chosen)
        binary = format(chosen, f"0{QUBIT_COUNT}b")
        self._measured_var.set(
            f"Last measurement: |{binary}>  (decimal {chosen}) - superposition collapsed."
        )
