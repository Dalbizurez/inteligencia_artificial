import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from filters.rgb_filter import RGBFilter
from filters.blur_filter import BlurFilter
from filters.edge_filter import EdgeFilter

# ── Palette ────────────────────────────────────────────────────────────────────
BG_DARK    = "#0d0f12"   # near-black canvas
BG_PANEL   = "#13161b"   # sidebar / panel background
BG_CARD    = "#1a1e26"   # individual control card
BORDER     = "#252a34"   # subtle card border
ACCENT     = "#00e5ff"   # electric-cyan primary accent
ACCENT2    = "#ff3d6b"   # hot-pink secondary accent (reset / danger)
ACCENT3    = "#7c3aed"   # violet tertiary (rotation)
TEXT_HI    = "#e8eaf0"   # primary text
TEXT_MID   = "#7a8294"   # secondary / label text
TEXT_LO    = "#3d4455"   # disabled / border hint

FONT_MONO  = ("Courier New", 9)
FONT_LABEL = ("Courier New", 8, "bold")
FONT_TITLE = ("Courier New", 10, "bold")
FONT_BTN   = ("Courier New", 9, "bold")


def _card(parent, title=None, **pack_kw):
    """Flat dark card with an optional top-label."""
    outer = tk.Frame(parent, bg=BORDER, bd=0)
    inner = tk.Frame(outer, bg=BG_CARD, bd=0, padx=10, pady=8)
    inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    if title:
        hdr = tk.Frame(inner, bg=BG_CARD)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="▸ " + title.upper(),
                 bg=BG_CARD, fg=ACCENT, font=FONT_TITLE).pack(side=tk.LEFT)
        tk.Frame(hdr, bg=ACCENT, height=1).pack(side=tk.LEFT,
                                                 fill=tk.X, expand=True, padx=(6, 0))
    outer.pack(**pack_kw)
    return inner


def _btn(parent, text, command, color=ACCENT, width=18):
    """Flat bordered button with hover effect."""
    f = tk.Frame(parent, bg=color, bd=0)
    b = tk.Button(
        f, text=text, command=command,
        bg=BG_CARD, fg=color, activebackground=color, activeforeground=BG_DARK,
        font=FONT_BTN, relief=tk.FLAT, bd=0, cursor="hand2",
        width=width, height=1, padx=6, pady=5,
    )
    b.pack(padx=1, pady=1)

    def _enter(e):  b.config(bg=color, fg=BG_DARK)
    def _leave(e):  b.config(bg=BG_CARD, fg=color)
    b.bind("<Enter>", _enter)
    b.bind("<Leave>", _leave)
    return f


def _slider(parent, from_, to, orient, command, length=160, accent=ACCENT):
    s = tk.Scale(
        parent, from_=from_, to=to, orient=orient, command=command,
        length=length, bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
        activebackground=accent, highlightthickness=0, bd=0,
        font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
        sliderlength=12, width=12,
    )
    return s


class MainView:

    def __init__(self, controller):
        self.controller = controller
        self.controller.set_view(self)

        self.root = tk.Tk()
        self.root.title("Image editor")
        self.root.geometry("1280x760")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self.panel = None
        self.filters = []
        self.current_image_tk = None
        self.setup_ui()

    # ── Layout ────────────────────────────────────────────────────────────────

    def setup_ui(self):
        # Top bar
        self._build_topbar()

        # Body
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Canvas column (left + bottom selection strip)
        self._build_canvas_column(body)

        # Sidebar (right)
        self._build_sidebar(body)

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=44)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="PHOTON", bg=BG_PANEL, fg=ACCENT,
                 font=("Courier New", 14, "bold")).pack(side=tk.LEFT, padx=16)
        tk.Label(bar, text="//  image editor", bg=BG_PANEL, fg=TEXT_MID,
                 font=("Courier New", 10)).pack(side=tk.LEFT)

        # right-side status dot
        tk.Label(bar, text="●  ready", bg=BG_PANEL, fg=ACCENT,
                 font=FONT_MONO).pack(side=tk.RIGHT, padx=16)

    def _build_canvas_column(self, parent):
        col = tk.Frame(parent, bg=BG_DARK)
        col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Image canvas
        canvas_card = _card(col, title="canvas", fill=tk.BOTH, expand=True, pady=(8, 6))
        self.panel = tk.Label(canvas_card, bg=BG_DARK, relief=tk.FLAT,
                              text="no image loaded", fg=TEXT_LO,
                              font=("Courier New", 11))
        self.panel.pack(fill=tk.BOTH, expand=True, pady=4)

        # Selection strip
        sel_card = _card(col, title="area selection", fill=tk.X, pady=(0, 0))
        self._add_selection_controls(sel_card)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=BG_PANEL, width=230)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar.pack_propagate(False)

        inner = tk.Frame(sidebar, bg=BG_PANEL, padx=10, pady=10)
        inner.pack(fill=tk.BOTH, expand=True)

        # Load button
        _btn(inner, "⬆  LOAD IMAGE", self.cargar_imagen,
             color=ACCENT).pack(fill=tk.X, pady=(0, 10))

        # Filters
        f_card = _card(inner, title="filters", fill=tk.X, pady=(0, 8))
        self._add_filters(f_card)

        # Rotation
        r_card = _card(inner, title="rotation", fill=tk.X, pady=(0, 8))
        self._add_rotation_controls(r_card)

        # Flip
        fl_card = _card(inner, title="flip", fill=tk.X, pady=(0, 8))
        self._add_transform_buttons(fl_card)

        # Reset
        _btn(inner, "✕  RESET ALL", self.reset_all,
             color=ACCENT2).pack(fill=tk.X, pady=(4, 0))

    # ── Filters ───────────────────────────────────────────────────────────────

    def _add_filters(self, parent):
        self.rgb_filter  = RGBFilter()
        self.blur_filter = BlurFilter()
        self.edge_filter = EdgeFilter()

        fm = self.controller._filter_manager
        fm.add_filter(self.rgb_filter)
        fm.add_filter(self.blur_filter)
        fm.add_filter(self.edge_filter)

        self.rgb_filter.get_control_widget(parent, self.apply_filters).pack(fill=tk.X, pady=2)
        self.blur_filter.get_control_widget(parent, self.apply_filters).pack(fill=tk.X, pady=2)
        self.edge_filter.get_control_widget(parent, self.apply_filters).pack(fill=tk.X, pady=2)

    # ── Rotation ──────────────────────────────────────────────────────────────

    def _add_rotation_controls(self, parent):
        btn_row = tk.Frame(parent, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=(0, 6))

        _btn(btn_row, "◀ 15°", lambda: self.rotate(-15),
             color=ACCENT3, width=7).pack(side=tk.LEFT, padx=(0, 4))
        _btn(btn_row, "15° ▶", lambda: self.rotate(15),
             color=ACCENT3, width=7).pack(side=tk.LEFT)

        self.angle_slider = _slider(parent, -180, 180, tk.HORIZONTAL,
                                    self.set_angle, length=190, accent=ACCENT3)
        self.angle_slider.pack(fill=tk.X)
        self.angle_slider.set(0)

        _btn(parent, "RESET ROTATION", self.reset_rotation,
             color=TEXT_MID, width=18).pack(pady=(6, 0))

    # ── Flip ──────────────────────────────────────────────────────────────────

    def _add_transform_buttons(self, parent):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(pady=4)
        _btn(row, "↔ H", self.controller.flip_horizontal,
             color=ACCENT, width=7).pack(side=tk.LEFT, padx=(0, 4))
        _btn(row, "↕ V", self.controller.flip_vertical,
             color=ACCENT, width=7).pack(side=tk.LEFT)

    # ── Area Selection ────────────────────────────────────────────────────────

    def _add_selection_controls(self, parent):
        # Shape radio row
        shape_row = tk.Frame(parent, bg=BG_CARD)
        shape_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(shape_row, text="SHAPE:", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack(side=tk.LEFT, padx=(0, 8))

        self.shape_var = tk.StringVar(value="ninguno")
        for label, val, clr in [("NONE", "ninguno", TEXT_MID),
                                 ("SQUARE", "cuadrado", ACCENT),
                                 ("CIRCLE", "circulo", ACCENT)]:
            rb = tk.Radiobutton(
                shape_row, text=label, variable=self.shape_var, value=val,
                command=self._on_shape_change,
                bg=BG_CARD, fg=clr, selectcolor=BG_DARK,
                activebackground=BG_CARD, activeforeground=clr,
                font=FONT_LABEL, relief=tk.FLAT, bd=0, cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=6)

        # Sliders row
        controls_row = tk.Frame(parent, bg=BG_CARD)
        controls_row.pack(fill=tk.X)

        # Position XY
        pos = tk.Frame(controls_row, bg=BG_CARD)
        pos.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        for axis in ("X", "Y"):
            tk.Label(pos, text=f"POS {axis}", bg=BG_CARD, fg=TEXT_MID,
                     font=FONT_LABEL).pack(anchor="w")
            sl = _slider(pos, 0, 100, tk.HORIZONTAL, self._on_position_change,
                         length=140, accent=ACCENT)
            sl.set(50)
            sl.pack(fill=tk.X, pady=(0, 4))
            setattr(self, f"{axis.lower()}_slider", sl)

        # Size
        sz = tk.Frame(controls_row, bg=BG_CARD)
        sz.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(sz, text="SIZE %", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack(anchor="w")
        self.size_slider = _slider(sz, 5, 50, tk.HORIZONTAL, self._on_size_change,
                                   length=140, accent=ACCENT)
        self.size_slider.set(20)
        self.size_slider.pack(fill=tk.X)

        # RGB vertical trio
        rgb_col = tk.Frame(controls_row, bg=BG_CARD)
        rgb_col.pack(side=tk.LEFT, padx=(0, 0))

        tk.Label(rgb_col, text="COLOR ADJ", bg=BG_CARD, fg=TEXT_MID,
                 font=FONT_LABEL).pack()

        trio = tk.Frame(rgb_col, bg=BG_CARD)
        trio.pack()

        for ch, clr in [("R", "#ff4d6a"), ("G", "#39ff7e"), ("B", "#4d9fff")]:
            col_f = tk.Frame(trio, bg=BG_CARD)
            col_f.pack(side=tk.LEFT, padx=4)
            tk.Label(col_f, text=ch, bg=BG_CARD, fg=clr,
                     font=("Courier New", 10, "bold")).pack()
            sl = tk.Scale(
                col_f, from_=-100, to=100, orient=tk.VERTICAL,
                command=self._on_color_change, length=90,
                bg=BG_CARD, fg=TEXT_HI, troughcolor=BG_DARK,
                activebackground=clr, highlightthickness=0, bd=0,
                font=FONT_MONO, relief=tk.FLAT, sliderrelief=tk.FLAT,
                sliderlength=12, width=12,
            )
            sl.set(0)
            sl.pack()
            setattr(self, f"{ch.lower()}_slider", sl)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_shape_change(self):
        shape = self.shape_var.get()
        if shape == "ninguno":
            self.controller.disable_selection()
        else:
            self.controller.set_selection_mode(shape)

    def _on_position_change(self, _=None):
        self.controller.set_selection_position(self.x_slider.get(), self.y_slider.get())

    def _on_size_change(self, _=None):
        self.controller.set_selection_size(self.size_slider.get())

    def _on_color_change(self, _=None):
        self.controller.set_selection_color(
            self.r_slider.get(), self.g_slider.get(), self.b_slider.get())

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[
            ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("All files", "*.*"),
        ])
        if ruta:
            self.controller.load_image(ruta)
            self.reset_all()

    def reset_all(self):
        for f in (self.rgb_filter, self.blur_filter, self.edge_filter):
            f.reset()
        self.angle_slider.set(0)
        self.shape_var.set("ninguno")
        self.x_slider.set(50)
        self.y_slider.set(50)
        self.size_slider.set(20)
        self.r_slider.set(0)
        self.g_slider.set(0)
        self.b_slider.set(0)
        self.controller.reset_filters()

    def reset_rotation(self):
        self.angle_slider.set(0)
        self.controller.reset_rotation()

    def rotate(self, delta):
        new_angle = self.controller.get_rotation_angle() + delta
        self.angle_slider.set(new_angle)
        self.controller.rotate(delta)

    def set_angle(self, value):
        self.controller.set_rotation_angle(float(value))

    def apply_filters(self):
        self.controller.apply_filters()

    def on_image_changed(self):
        self.root.after(100, self.update_display)

    def update_display(self):
        img = self.controller.get_current_image()
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            w, h = img_pil.size
            mw, mh = 560, 430
            if w > mw or h > mh:
                ratio = min(mw / w, mh / h)
                img_pil = img_pil.resize((int(w * ratio), int(h * ratio)),
                                         Image.Resampling.LANCZOS)
            self.current_image_tk = ImageTk.PhotoImage(img_pil)
            self.panel.config(image=self.current_image_tk, text="")
            self.panel.image = self.current_image_tk

    def run(self):
        self.root.mainloop()