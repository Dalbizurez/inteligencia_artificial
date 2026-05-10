import cv2
import numpy as np
import tkinter as tk
from typing import Any
from .base_filter import ImageFilter

# ── Palette (mirrors main_view.py) ────────────────────────────────────────────
BG_CARD      = "#1a1e26"
BG_DARK      = "#0d0f12"
ACCENT_EDGE  = "#f59e0b"   # amber — visually distinct from blur (cyan) and RGB (per-channel)
TEXT_HI      = "#e8eaf0"
TEXT_MID     = "#7a8294"

FONT_MONO  = ("Courier New", 9)
FONT_LABEL = ("Courier New", 8, "bold")
FONT_TITLE = ("Courier New", 9, "bold")


class EdgeFilter(ImageFilter):

    def __init__(self):
        super().__init__()
        self._params = {'intensity': 0, 'axis_x': True, 'axis_y': True}

    # ── Core logic (unchanged) ─────────────────────────────────────────────

    def apply(self, image: np.ndarray) -> np.ndarray:
        if not self._enabled:
            return image
        intensity = self._params['intensity']
        if intensity == 0:
            return image
        axis_x = self._params['axis_x']
        axis_y = self._params['axis_y']
        if not (axis_x or axis_y):
            return image

        gray   = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3) if axis_x else 0
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3) if axis_y else 0
        edges   = np.abs(sobel_x) + np.abs(sobel_y)
        factor  = intensity / 50.0
        edges   = np.clip(edges * factor, 0, 255).astype(np.uint8)
        edges_3c = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.addWeighted(image, 0.7, edges_3c, 0.3, 0)

    # ── Widget ────────────────────────────────────────────────────────────

    def get_control_widget(self, parent, callback) -> Any:
        # 1-px accent border → dark card
        border = tk.Frame(parent, bg=ACCENT_EDGE, bd=0)
        card   = tk.Frame(border, bg=BG_CARD, bd=0, padx=8, pady=6)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(card, bg=BG_CARD)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="▸ EDGE DETECT",
                 bg=BG_CARD, fg=ACCENT_EDGE, font=FONT_TITLE).pack(side=tk.LEFT)
        tk.Frame(hdr, bg=ACCENT_EDGE, height=1).pack(side=tk.LEFT,
                                                       fill=tk.X, expand=True, padx=(6, 0))

        # Intensity row
        int_row = tk.Frame(card, bg=BG_CARD)
        int_row.pack(fill=tk.X, pady=(0, 4))

        tk.Label(int_row, text="INTENSITY", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack(side=tk.LEFT, padx=(0, 6))

        slider = tk.Scale(
            int_row, from_=0, to=100, orient=tk.HORIZONTAL,
            command=lambda v: self._update_param('intensity', int(v), callback),
            bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
            activebackground=ACCENT_EDGE, highlightthickness=0, bd=0,
            font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
            sliderlength=12, width=10, length=110,
        )
        slider.set(0)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._edge_val_lbl = tk.Label(int_row, text=" 0 ", bg=BG_CARD, fg=ACCENT_EDGE,
                                      font=FONT_MONO, width=3)
        self._edge_val_lbl.pack(side=tk.LEFT, padx=(4, 0))

        # Axis toggle row
        axis_row = tk.Frame(card, bg=BG_CARD)
        axis_row.pack(fill=tk.X)

        tk.Label(axis_row, text="AXIS:", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack(side=tk.LEFT, padx=(0, 8))

        var_x = tk.BooleanVar(value=self._params['axis_x'])
        var_y = tk.BooleanVar(value=self._params['axis_y'])

        for label, var, key in [("X", var_x, 'axis_x'), ("Y", var_y, 'axis_y')]:
            chk = tk.Checkbutton(
                axis_row, text=label, variable=var,
                command=lambda k=key, v=var: self._update_param(k, v.get(), callback),
                bg=BG_CARD, fg=ACCENT_EDGE, selectcolor=BG_DARK,
                activebackground=BG_CARD, activeforeground=ACCENT_EDGE,
                font=FONT_LABEL, relief=tk.FLAT, bd=0, cursor="hand2",
            )
            chk.pack(side=tk.LEFT, padx=6)

        self._control_widgets = {'slider': slider, 'var_x': var_x, 'var_y': var_y}
        return border

    # ── Helpers ───────────────────────────────────────────────────────────

    def _update_param(self, key: str, value, callback):
        self._params[key] = value
        if key == 'intensity' and hasattr(self, '_edge_val_lbl'):
            self._edge_val_lbl.config(text=f" {value} ")
        callback()

    def reset(self):
        self._params = {'intensity': 0, 'axis_x': True, 'axis_y': True}
        if hasattr(self, '_control_widgets'):
            self._control_widgets['slider'].set(0)
            self._control_widgets['var_x'].set(True)
            self._control_widgets['var_y'].set(True)
        if hasattr(self, '_edge_val_lbl'):
            self._edge_val_lbl.config(text=" 0 ")