import numpy as np
import tkinter as tk
from typing import Any
from .base_filter import ImageFilter

# ── Palette (mirrors main_view.py) ────────────────────────────────────────────
BG_CARD  = "#1a1e26"
BG_DARK  = "#0d0f12"
ACCENT   = "#00e5ff"
TEXT_HI  = "#e8eaf0"
TEXT_MID = "#7a8294"

FONT_MONO  = ("Courier New", 9)
FONT_LABEL = ("Courier New", 8, "bold")
FONT_TITLE = ("Courier New", 9, "bold")

CH_COLORS = {"R": "#ff4d6a", "G": "#39ff7e", "B": "#4d9fff"}


class RGBFilter(ImageFilter):

    def __init__(self):
        super().__init__()
        self._params = {'R': 0, 'G': 0, 'B': 0}

    # ── Core logic (unchanged) ─────────────────────────────────────────────

    def apply(self, image: np.ndarray) -> np.ndarray:
        if not self._enabled:
            return image
        result = image.astype(np.int16)
        result[:, :, 2] += self._params['R']
        result[:, :, 1] += self._params['G']
        result[:, :, 0] += self._params['B']
        return np.clip(result, 0, 255).astype(np.uint8)

    # ── Widget ────────────────────────────────────────────────────────────

    def get_control_widget(self, parent, callback) -> Any:
        # 1-px accent border → dark card
        border = tk.Frame(parent, bg=ACCENT, bd=0)
        card   = tk.Frame(border, bg=BG_CARD, bd=0, padx=8, pady=6)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(card, bg=BG_CARD)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="▸ RGB  ADJUST",
                 bg=BG_CARD, fg=ACCENT, font=FONT_TITLE).pack(side=tk.LEFT)
        tk.Frame(hdr, bg=ACCENT, height=1).pack(side=tk.LEFT,
                                                  fill=tk.X, expand=True, padx=(6, 0))

        # One row per channel
        sliders: dict = {}
        val_labels: dict = {}

        for ch in ("R", "G", "B"):
            clr = CH_COLORS[ch]
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill=tk.X, pady=2)

            # Coloured channel badge
            tk.Label(row, text=ch, bg=clr, fg=BG_CARD,
                     font=("Courier New", 8, "bold"), width=2, padx=2).pack(side=tk.LEFT, padx=(0, 6))

            slider = tk.Scale(
                row, from_=-100, to=100, orient=tk.HORIZONTAL,
                command=lambda v, k=ch: self._update_param(k, int(v), callback),
                bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
                activebackground=clr, highlightthickness=0, bd=0,
                font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
                sliderlength=12, width=10, length=120,
            )
            slider.set(0)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

            val_lbl = tk.Label(row, text=" +0 ", bg=BG_CARD, fg=clr,
                               font=FONT_MONO, width=5)
            val_lbl.pack(side=tk.LEFT, padx=(4, 0))

            sliders[ch]    = slider
            val_labels[ch] = val_lbl

        self._control_widgets = sliders
        self._val_labels      = val_labels
        return border

    # ── Helpers ───────────────────────────────────────────────────────────

    def _update_param(self, key: str, value: int, callback):
        self._params[key] = value
        if hasattr(self, '_val_labels') and key in self._val_labels:
            sign = "+" if value >= 0 else ""
            self._val_labels[key].config(text=f" {sign}{value} ")
        callback()

    def reset(self):
        for key in self._params:
            self._params[key] = 0
        if hasattr(self, '_control_widgets'):
            for key, slider in self._control_widgets.items():
                slider.set(0)
        if hasattr(self, '_val_labels'):
            for lbl in self._val_labels.values():
                lbl.config(text=" +0 ")