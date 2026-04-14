"""Shared color palette and ttk styling."""
from tkinter import ttk

COLORS = {
    "bg":          "#0f1115",
    "panel":       "#181b22",
    "panel2":      "#222631",
    "border":      "#2c3140",
    "text":        "#e7e9ee",
    "text_dim":    "#a0a6b4",
    "accent":      "#4f8cff",
    "accent2":     "#8a5bff",
    "good":        "#4ade80",
    "bad":         "#ef4444",
    # CS-like rarity palette
    "blue":        "#4b69ff",
    "purple":      "#8847ff",
    "pink":        "#d32ce6",
    "red":         "#eb4b4b",
    "gold":        "#ffd700",
}


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
        tabmargins=[8, 6, 8, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["panel"],
        foreground=COLORS["text_dim"],
        padding=[18, 10],
        borderwidth=0,
        font=("Segoe UI", 11, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["panel2"])],
        foreground=[("selected", COLORS["text"])],
    )

    style.configure(
        "TFrame",
        background=COLORS["bg"],
    )
    style.configure(
        "Panel.TFrame",
        background=COLORS["panel"],
        relief="flat",
    )
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Panel.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 16, "bold"),
    )
    style.configure(
        "PanelTitle.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Segoe UI", 13, "bold"),
    )
    style.configure(
        "Dim.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text_dim"],
        font=("Segoe UI", 9),
    )

    style.configure(
        "TButton",
        background=COLORS["panel2"],
        foreground=COLORS["text"],
        borderwidth=0,
        focusthickness=0,
        padding=[12, 8],
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", COLORS["accent"])],
        foreground=[("active", "#ffffff")],
    )

    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground="#ffffff",
        padding=[18, 12],
        font=("Segoe UI", 12, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("active", COLORS["accent2"])],
    )

    style.configure(
        "Horizontal.TScale",
        background=COLORS["panel"],
        troughcolor=COLORS["panel2"],
    )

    style.configure(
        "TSeparator",
        background=COLORS["border"],
    )
