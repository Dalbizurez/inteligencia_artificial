import cv2
import numpy as np
import tkinter as tk
from typing import Any
from .base_filter import ImageFilter

# ── Palette (mirrors main_view.py) ────────────────────────────────────────────
BG_CARD     = "#1a1e26"
BG_DARK     = "#0d0f12"
ACCENT_BLUR = "#00e5ff"   # cyan — matches primary accent
TEXT_HI     = "#e8eaf0"
TEXT_MID    = "#7a8294"

FONT_MONO  = ("Courier New", 9)
FONT_LABEL = ("Courier New", 8, "bold")
FONT_TITLE = ("Courier New", 9, "bold")


class BlurFilter(ImageFilter):

    def __init__(self):
        super().__init__()
        self._params = {'kernel_size': 1}

    # ── Core logic (unchanged) ─────────────────────────────────────────────

    def apply(self, image: np.ndarray) -> np.ndarray:
        if not self._enabled:
            return image
        k = self._params['kernel_size']
        if k <= 1:
            return image
        k = k if k % 2 else k + 1
        return cv2.GaussianBlur(image, (k, k), 0)

    # ── Widget ────────────────────────────────────────────────────────────

    def get_control_widget(self, parent, callback) -> Any:
        # 1-px accent border → dark card
        border = tk.Frame(parent, bg=ACCENT_BLUR, bd=0)
        card   = tk.Frame(border, bg=BG_CARD, bd=0, padx=8, pady=6)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(card, bg=BG_CARD)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="▸ BLUR",
                 bg=BG_CARD, fg=ACCENT_BLUR, font=FONT_TITLE).pack(side=tk.LEFT)
        tk.Frame(hdr, bg=ACCENT_BLUR, height=1).pack(side=tk.LEFT,
                                                       fill=tk.X, expand=True, padx=(6, 0))

        # Slider row
        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill=tk.X)

        tk.Label(row, text="RADIUS", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack(side=tk.LEFT, padx=(0, 6))

        slider = tk.Scale(
            row, from_=1, to=25, orient=tk.HORIZONTAL,
            command=lambda v: self._update_param(int(v), callback),
            bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
            activebackground=ACCENT_BLUR, highlightthickness=0, bd=0,
            font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
            sliderlength=12, width=10, length=120,
        )
        slider.set(1)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Live readout
        self._blur_val_lbl = tk.Label(row, text=" 1 ", bg=BG_CARD, fg=ACCENT_BLUR,
                                      font=FONT_MONO, width=3)
        self._blur_val_lbl.pack(side=tk.LEFT, padx=(4, 0))

        self._control_slider = slider
        return border

    # ── Helpers ───────────────────────────────────────────────────────────

    def _update_param(self, value: int, callback):
        self._params['kernel_size'] = value
        if hasattr(self, '_blur_val_lbl'):
            self._blur_val_lbl.config(text=f" {value} ")
        callback()

    def reset(self):
        self._params['kernel_size'] = 1
        if hasattr(self, '_control_slider'):
            self._control_slider.set(1)
        if hasattr(self, '_blur_val_lbl'):
            self._blur_val_lbl.config(text=" 1 ")