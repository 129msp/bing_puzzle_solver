import tkinter as tk
from tkinter import messagebox
import threading
import time
import heapq
import random
import pyautogui

# ──────────────────────────────────────────────────────
#  SOLVER LOGIC
# ──────────────────────────────────────────────────────

GOAL_STATE  = (1, 2, 3, 4, 5, 6, 7, 8, 0)
CLICK_DELAY = 0.5

def manhattan(state):
    dist = 0
    for i, val in enumerate(state):
        if val == 0:
            continue
        gi = val - 1
        dist += abs(i // 3 - gi // 3) + abs(i % 3 - gi % 3)
    return dist

def neighbors(state):
    result = []
    ei = state.index(0)
    er, ec = divmod(ei, 3)
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = er+dr, ec+dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            ni = nr*3 + nc
            s = list(state)
            s[ei], s[ni] = s[ni], s[ei]
            result.append((tuple(s), s[ei]))
    return result

def a_star(state):
    if state == GOAL_STATE:
        return []
    heap = [(manhattan(state), 0, state, [])]
    seen = set()
    while heap:
        f, g, cur, path = heapq.heappop(heap)
        if cur in seen:
            continue
        seen.add(cur)
        if cur == GOAL_STATE:
            return path
        for ns, tile in neighbors(cur):
            if ns not in seen:
                ng = g + 1
                heapq.heappush(heap, (ng + manhattan(ns), ng, ns, path + [tile]))
    return None

def build_centers(x1, y1, x2, y2):
    rw = x2 - x1
    rh = y2 - y1
    cw = rw // 3
    ch = rh // 3
    centers = []
    for r in range(3):
        for c in range(3):
            cx = x1 + c*cw + cw//2
            cy = y1 + r*ch + ch//2
            centers.append((cx, cy))
    return centers, cw, ch

# ──────────────────────────────────────────────────────
#  COLOR PALETTE
# ──────────────────────────────────────────────────────

BG          = "#0f0f13"
BG_CARD     = "#1a1a24"
BG_INPUT    = "#13131c"
BORDER      = "#2a2a3a"
ACCENT      = "#6c63ff"
ACCENT_DIM  = "#3d3870"
TEXT        = "#e8e8f0"
TEXT_DIM    = "#7878a0"
TEXT_LABEL  = "#a0a0c0"
SUCCESS     = "#3ddc84"
WARNING     = "#ffb347"
ERROR       = "#ff6b6b"
STEP_FG     = "#c0beff"

# ──────────────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────────────

class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bing Puzzle Solver")
        self.resizable(True, True)
        self.minsize(460, 600)
        self.configure(bg=BG)

        # State
        self.tile_vars  = [tk.StringVar() for _ in range(9)]
        self.coord_x1   = tk.IntVar(value=0)
        self.coord_y1   = tk.IntVar(value=0)
        self.coord_x2   = tk.IntVar(value=0)
        self.coord_y2   = tk.IntVar(value=0)
        self.exec_mode  = tk.StringVar(value="1")
        self.running    = False

        self._build_ui()
        self._center_window()

    # ── Layout ────────────────────────────────────────

    def _build_ui(self):
        PAD = 20

        # Fixed header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD, pady=(PAD, 0))

        tk.Label(
            header, text="Bing Puzzle Solver",
            font=("Segoe UI", 18, "bold"),
            bg=BG, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            header, text="Made by Stephan  |  PyAutoGUI Edition",
            font=("Segoe UI", 9),
            bg=BG, fg=TEXT_DIM
        ).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=PAD, pady=12)

        # Scrollable area
        scroll_container = tk.Frame(self, bg=BG)
        scroll_container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", bg=BG_CARD,
                                  troughcolor=BG_INPUT, activebackground=ACCENT_DIM)
        scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(
            scroll_container, bg=BG,
            yscrollcommand=scrollbar.set,
            highlightthickness=0, bd=0
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._canvas.yview)

        # Inner frame inside canvas
        self._inner = tk.Frame(self._canvas, bg=BG)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        # Resize inner frame width when canvas resizes
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._inner.bind("<Configure>",  self._on_inner_configure)

        # Mousewheel scroll
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Content inside inner
        body = self._inner

        # Step 1
        s1 = self._card(body, "Step 1: Masukkan state puzzle")
        tk.Label(
            s1,
            text="Baca angka dari kiri-atas ke kanan-bawah. Gunakan 0 untuk kotak kosong.",
            font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_DIM, wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0, 12))

        grid_frame = tk.Frame(s1, bg=BG_CARD)
        grid_frame.pack()

        self.tile_entries = []
        for i in range(9):
            r, c = divmod(i, 3)
            e = tk.Entry(
                grid_frame,
                textvariable=self.tile_vars[i],
                width=4,
                font=("Segoe UI", 20, "bold"),
                justify="center",
                bg=BG_INPUT, fg=TEXT,
                insertbackground=ACCENT,
                relief="flat",
                highlightthickness=2,
                highlightbackground=BORDER,
                highlightcolor=ACCENT
            )
            e.grid(row=r, column=c, padx=5, pady=5, ipady=8)
            e.bind("<FocusIn>",  lambda ev, entry=e: self._on_focus_in(entry))
            e.bind("<FocusOut>", lambda ev, entry=e: self._on_focus_out(entry))
            e.bind("<KeyRelease>", lambda ev, idx=i: self._auto_advance(ev, idx))
            self.tile_entries.append(e)

        btn_row = tk.Frame(s1, bg=BG_CARD)
        btn_row.pack(pady=(12, 0))
        self._btn(btn_row, "Acak Contoh", self._fill_example, style="ghost").pack(side="left", padx=(0, 8))
        self._btn(btn_row, "Reset",        self._reset_grid,  style="ghost").pack(side="left")

        self._divider(body)

        # Step 2
        s2 = self._card(body, "Step 2: Deteksi koordinat puzzle")
        tk.Label(
            s2,
            text="Klik tombol di bawah lalu arahkan mouse ke sudut puzzle.",
            font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_DIM, wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0, 2))
        tk.Label(
            s2,
            text="JANGAN KLIK. Cukup arahkan mouse, dan tunggu hingga panel terbuka kembali.",
            font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=WARNING, wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0, 12))

        coord_row = tk.Frame(s2, bg=BG_CARD)
        coord_row.pack(fill="x")
        self._btn(coord_row, "Tangkap Kiri-Atas",   lambda: self._capture_corner("tl"), style="ghost").pack(side="left", padx=(0, 8))
        self._btn(coord_row, "Tangkap Kanan-Bawah", lambda: self._capture_corner("br"), style="ghost").pack(side="left")

        self.coord_label = tk.Label(
            s2, text="Belum ada koordinat.",
            font=("Segoe UI", 9, "italic"),
            bg=BG_CARD, fg=TEXT_DIM
        )
        self.coord_label.pack(anchor="w", pady=(10, 0))

        self._divider(body)

        # Step 3
        s3 = self._card(body, "Step 3: Pilih mode eksekusi")
        for label, val in [
            ("God Mode (cepat, langsung selesai)", "1"),
            ("Human Mode (simulasi perilaku manusia)", "2"),
        ]:
            tk.Radiobutton(
                s3, text=label, variable=self.exec_mode, value=val,
                font=("Segoe UI", 10),
                bg=BG_CARD, fg=TEXT_LABEL,
                selectcolor=BG_INPUT,
                activebackground=BG_CARD, activeforeground=TEXT,
                relief="flat", bd=0, cursor="hand2"
            ).pack(anchor="w", pady=2)

        self._divider(body)

        # Solve Button
        solve_frame = tk.Frame(body, bg=BG)
        solve_frame.pack(padx=PAD, pady=(0, PAD), fill="x")
        self.solve_btn = self._btn(solve_frame, "Solve Puzzle", self._on_solve, style="primary")
        self.solve_btn.pack(fill="x", ipady=10)

        # Log
        log_frame = tk.Frame(body, bg=BG_CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        log_frame.pack(padx=PAD, pady=(0, PAD), fill="both")

        tk.Label(
            log_frame, text="Log", font=("Segoe UI", 8, "bold"),
            bg=BG_CARD, fg=TEXT_DIM
        ).pack(anchor="w", padx=10, pady=(6, 0))

        self.log_text = tk.Text(
            log_frame, height=8, state="disabled",
            bg=BG_INPUT, fg=STEP_FG,
            font=("Consolas", 9),
            relief="flat", bd=0,
            insertbackground=ACCENT,
            padx=10, pady=6,
            wrap="word"
        )
        self.log_text.pack(fill="both", pady=(0, 4))
        self.log_text.tag_config("ok",   foreground=SUCCESS)
        self.log_text.tag_config("warn", foreground=WARNING)
        self.log_text.tag_config("err",  foreground=ERROR)
        self.log_text.tag_config("dim",  foreground=TEXT_DIM)

    def _on_canvas_configure(self, event):
        """Saat canvas di-resize, lebarkan inner frame agar mengisi lebar."""
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_inner_configure(self, event):
        """Update scroll region saat konten bertambah/berubah ukuran."""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    # Helpers: Widgets

    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(padx=20, pady=(0, 0), fill="x")

        tk.Label(
            outer, text=title,
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg=ACCENT
        ).pack(anchor="w", pady=(0, 6))

        inner = tk.Frame(outer, bg=BG_CARD, padx=16, pady=14,
                         highlightthickness=1, highlightbackground=BORDER)
        inner.pack(fill="x")
        return inner

    def _divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

    def _btn(self, parent, text, command, style="ghost"):
        if style == "primary":
            b = tk.Button(
                parent, text=text, command=command,
                font=("Segoe UI", 11, "bold"),
                bg=ACCENT, fg="white",
                activebackground=ACCENT_DIM, activeforeground="white",
                relief="flat", bd=0, cursor="hand2"
            )
        else:
            b = tk.Button(
                parent, text=text, command=command,
                font=("Segoe UI", 9),
                bg=BG_INPUT, fg=TEXT_LABEL,
                activebackground=BORDER, activeforeground=TEXT,
                relief="flat", bd=0, cursor="hand2",
                padx=12, pady=6,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT
            )
        return b

    def _on_focus_in(self, entry):
        entry.config(highlightbackground=ACCENT)

    def _on_focus_out(self, entry):
        entry.config(highlightbackground=BORDER)

    def _auto_advance(self, event, idx):
        """Pindah fokus ke tile berikutnya setelah isi 1 karakter."""
        val = self.tile_vars[idx].get()
        if len(val) >= 1 and idx < 8:
            self.tile_entries[idx + 1].focus_set()
            self.tile_entries[idx + 1].select_range(0, "end")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # Helpers: Log

    def _log(self, msg, tag=None):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n", tag or "")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _log_clear(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # Actions

    def _fill_example(self):
        example = "5 2 3 8 1 6 4 7 0".split()
        for i, v in enumerate(example):
            self.tile_vars[i].set(v)

    def _reset_grid(self):
        for v in self.tile_vars:
            v.set("")
        self.tile_entries[0].focus_set()

    def _capture_corner(self, corner):
        """Minimize window, hitung mundur, capture posisi mouse.
        Tidak perlu diklik — cukup hover mouse ke sudut puzzle.
        """
        label = "kiri-atas" if corner == "tl" else "kanan-bawah"
        self._log(f"Arahkan mouse ke sudut {label}  —  JANGAN KLIK, cukup hover.", "warn")
        self._log("Koordinat otomatis tercatat setelah 3 detik.", "dim")
        self._saved_geometry = self.geometry()
        self.iconify()
        self._countdown(corner, 3)

    def _countdown(self, corner, remaining):
        """Hitung mundur sambil update title bar, lalu capture."""
        if remaining > 0:
            self.title(f"Bing Puzzle Solver  —  Jangan klik! Tercatat dalam {remaining}...")
            self.after(1000, lambda: self._countdown(corner, remaining - 1))
        else:
            self.title("Bing Puzzle Solver")
            self._do_capture(corner)

    def _do_capture(self, corner):
        x, y = pyautogui.position()
        self.state('normal')          # paksa restore dari minimize (Windows-safe)
        self.update()                 # flush sebelum ubah geometry
        if hasattr(self, '_saved_geometry'):
            self.geometry(self._saved_geometry)
        self.lift()
        self.focus_force()

        if corner == "tl":
            self.coord_x1.set(x)
            self.coord_y1.set(y)
        else:
            self.coord_x2.set(x)
            self.coord_y2.set(y)

        self._update_coord_label()
        self._log(f"Tertangkap  :  ({x}, {y})  [sudut {'kiri-atas' if corner == 'tl' else 'kanan-bawah'}]", "ok")

    def _update_coord_label(self):
        x1, y1 = self.coord_x1.get(), self.coord_y1.get()
        x2, y2 = self.coord_x2.get(), self.coord_y2.get()
        if x1 == 0 and y1 == 0:
            self.coord_label.config(text="Belum ada koordinat.", fg=TEXT_DIM)
        elif x2 == 0 and y2 == 0:
            self.coord_label.config(text=f"Kiri-atas: ({x1}, {y1})  |  Kanan-bawah: belum", fg=WARNING)
        else:
            w, h = x2 - x1, y2 - y1
            self.coord_label.config(
                text=f"({x1}, {y1})  ->  ({x2}, {y2})   [{w} x {h} px]",
                fg=SUCCESS
            )

    def _on_solve(self):
        if self.running:
            return

        # Baca state
        raw = []
        for i, v in enumerate(self.tile_vars):
            val = v.get().strip()
            if not val.isdigit():
                messagebox.showerror("Input Error", f"Tile #{i+1} harus angka (0-8).")
                return
            raw.append(int(val))

        state = tuple(raw)
        if sorted(state) != list(range(9)):
            messagebox.showerror("Input Error", "Harus ada angka 0 hingga 8, masing-masing sekali.")
            return

        # Validasi koordinat
        x1, y1 = self.coord_x1.get(), self.coord_y1.get()
        x2, y2 = self.coord_x2.get(), self.coord_y2.get()
        if x2 <= x1 or y2 <= y1:
            messagebox.showerror("Koordinat Error", "Tangkap kedua sudut puzzle terlebih dahulu.")
            return

        # Validasi solvability
        flat = [x for x in state if x != 0]
        inversions = sum(
            1 for i in range(len(flat))
            for j in range(i+1, len(flat))
            if flat[i] > flat[j]
        )
        if inversions % 2 != 0:
            messagebox.showerror("Puzzle Error", "Puzzle ini tidak dapat diselesaikan.\nPastikan state sudah benar.")
            return

        if state == GOAL_STATE:
            messagebox.showinfo("Info", "Puzzle sudah dalam kondisi selesai.")
            return

        mode = self.exec_mode.get()
        self._log_clear()
        self._log("Menghitung solusi A*...", "dim")
        self.solve_btn.config(state="disabled", text="Berjalan...")
        self.running = True

        threading.Thread(
            target=self._run_solver,
            args=(state, x1, y1, x2, y2, mode),
            daemon=True
        ).start()

    def _run_solver(self, state, x1, y1, x2, y2, mode):
        solution = a_star(state)
        if not solution:
            self.after(0, lambda: self._log("Solusi tidak ditemukan.", "err"))
            self.after(0, self._reset_btn)
            return

        self.after(0, lambda: self._log(f"Solusi ditemukan  :  {len(solution)} langkah", "ok"))
        self.after(0, lambda: self._log(f"Urutan tile       :  {solution}", "dim"))

        centers, cw, ch = build_centers(x1, y1, x2, y2)

        time.sleep(1)   # beri waktu user siap

        cur_state = state
        total = len(solution)
        for step, tile_num in enumerate(solution, 1):
            tile_pos = cur_state.index(tile_num)
            scr_x, scr_y = centers[tile_pos]

            if mode == "1":
                jx = random.randint(-4, 4)
                jy = random.randint(-4, 4)
                tx, ty = scr_x + jx, scr_y + jy
                pyautogui.moveTo(tx, ty, duration=random.uniform(0.08, 0.15))
                time.sleep(random.uniform(0.03, 0.08))
                pyautogui.click()
                msg = f"Step {step:>2}/{total}  |  tile [{tile_num}]  ->  ({tx}, {ty})"
                self.after(0, lambda m=msg: self._log(m))
                time.sleep(CLICK_DELAY + random.uniform(-0.05, 0.1))

            else:
                jx = random.randint(-8, 8)
                jy = random.randint(-8, 8)
                tx, ty = scr_x + jx, scr_y + jy

                think = random.random()
                if think < 0.35:
                    wx = scr_x + random.randint(-cw, cw)
                    wy = scr_y + random.randint(-ch, ch)
                    pyautogui.moveTo(wx, wy, duration=random.uniform(0.2, 0.5))
                    time.sleep(random.uniform(0.3, 0.9))
                elif think < 0.55:
                    time.sleep(random.uniform(0.4, 1.2))

                pyautogui.moveTo(tx, ty, duration=random.uniform(0.18, 0.45))
                time.sleep(random.uniform(0.05, 0.18))
                if random.random() < 0.2:
                    time.sleep(random.uniform(0.2, 0.6))
                pyautogui.click()

                msg = f"Step {step:>2}/{total}  |  tile [{tile_num}]  ->  ({tx}, {ty})"
                self.after(0, lambda m=msg: self._log(m))

                base_delay = random.uniform(0.55, 1.1)
                if random.random() < 0.12:
                    extra = random.uniform(1.0, 2.5)
                    self.after(0, lambda e=extra: self._log(f"             (pause {e:.1f}s)", "dim"))
                    base_delay += extra
                time.sleep(base_delay)

            # Update state
            for ns, t in neighbors(cur_state):
                if t == tile_num:
                    cur_state = ns
                    break

        self.after(0, lambda: self._log("Selesai! Puzzle berhasil diselesaikan.", "ok"))
        self.after(0, self._reset_btn)

    def _reset_btn(self):
        self.running = False
        self.solve_btn.config(state="normal", text="Solve Puzzle")


# ──────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    app = PuzzleApp()
    app.mainloop()
