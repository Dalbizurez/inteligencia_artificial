import tkinter as tk
from typing import Callable, Dict

# ── Shared palette (mirrors main_view.py) ─────────────────────────────────────
BG_CARD   = "#1a1e26"
BG_DARK   = "#0d0f12"
ACCENT    = "#00e5ff"
TEXT_HI   = "#e8eaf0"
TEXT_MID  = "#7a8294"

FONT_MONO  = ("Courier New", 9)
FONT_LABEL = ("Courier New", 8, "bold")
FONT_TITLE = ("Courier New", 9, "bold")

# Per-channel accent colours
CH_COLORS = {"R": "#ff4d6a", "G": "#39ff7e", "B": "#4d9fff"}


class RGBControls:
    """
    Horizontal RGB slider bank.
    Each channel gets its own accent colour; the whole widget is themed
    to match the dark-industrial MainView palette.
    """

    def __init__(self, parent: tk.Widget, callback: Callable):
        self.callback = callback
        self.sliders: Dict[str, tk.Scale] = {}
        self._build(parent)

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self, parent: tk.Widget):
        # Outer 1-px accent border → inner card
        border = tk.Frame(parent, bg=ACCENT, bd=0)
        self.frame = tk.Frame(border, bg=BG_CARD, bd=0, padx=8, pady=6)
        self.frame.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        # Header row
        hdr = tk.Frame(self.frame, bg=BG_CARD)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="▸ RGB  ADJUST",
                 bg=BG_CARD, fg=ACCENT, font=FONT_TITLE).pack(side=tk.LEFT)
        tk.Frame(hdr, bg=ACCENT, height=1).pack(side=tk.LEFT,
                                                  fill=tk.X, expand=True, padx=(6, 0))

        # One row per channel
        for ch in ("R", "G", "B"):
            clr = CH_COLORS[ch]
            row = tk.Frame(self.frame, bg=BG_CARD)
            row.pack(fill=tk.X, pady=2)

            # Channel badge
            badge = tk.Label(row, text=ch, bg=clr, fg=BG_CARD,
                             font=("Courier New", 8, "bold"),
                             width=2, padx=2)
            badge.pack(side=tk.LEFT, padx=(0, 6))

            # Slider
            sl = tk.Scale(
                row, from_=-100, to=100, orient=tk.HORIZONTAL,
                command=lambda v, k=ch: self._on_change(k, int(v)),
                bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
                activebackground=clr, highlightthickness=0, bd=0,
                font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
                sliderlength=12, width=10, length=160,
            )
            sl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.sliders[ch] = sl

            # Live value readout
            val_lbl = tk.Label(row, text=" +0 ", bg=BG_CARD, fg=clr,
                               font=FONT_MONO, width=5)
            val_lbl.pack(side=tk.LEFT, padx=(4, 0))

            # Keep a reference so we can update it
            sl._val_label = val_lbl

        self._outer = border   # expose for pack / grid

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_change(self, key: str, value: int):
        # Update live readout
        sl = self.sliders.get(key)
        if sl and hasattr(sl, "_val_label"):
            sign = "+" if value >= 0 else ""
            sl._val_label.config(text=f"{sign}{value}")

        if self.callback:
            self.callback(key, value)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_value(self, key: str) -> int:
        sl = self.sliders.get(key)
        return int(sl.get()) if sl else 0

    def set_value(self, key: str, value: int):
        sl = self.sliders.get(key)
        if sl:
            sl.set(value)
            sign = "+" if value >= 0 else ""
            if hasattr(sl, "_val_label"):
                sl._val_label.config(text=f"{sign}{value}")

    def reset(self):
        for key in self.sliders:
            self.set_value(key, 0)

    # Geometry delegation — keeps call-sites identical to before
    def pack(self, **kwargs):
        self._outer.pack(**kwargs)

    def grid(self, **kwargs):
        self._outer.grid(**kwargs)

    def place(self, **kwargs):
        self._outer.place(**kwargs)