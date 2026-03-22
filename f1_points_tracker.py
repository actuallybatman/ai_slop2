import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ─── F1 Points System ────────────────────────────────────────────────────────
F1_POINTS = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8,  7: 6,  8: 4,  9: 2,  10: 1,
    11: 0, 12: 0, 13: 0, 14: 0, 15: 0,
    16: 0, 17: 0, 18: 0, 19: 0, 20: 0,
}

DRIVERS       = ["Shaayeq", "Niladri", "Parijat"]
DRIVER_COLORS = ["#E8002D", "#00BFFF", "#39FF14"]
DRIVER_BG     = ["#1E0005", "#00101A", "#001A03"]

F1_DARK   = "#0A0A0A"
F1_CARBON = "#141414"
F1_PANEL  = "#1C1C1C"
F1_BORDER = "#2A2A2A"
F1_SILVER = "#808080"
F1_WHITE  = "#F0F0F0"
F1_GOLD   = "#FFD700"
F1_RED    = "#E8002D"

# ─── Database ─────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            race_num   INTEGER NOT NULL,
            pos_s      INTEGER NOT NULL,
            pos_n      INTEGER NOT NULL,
            pos_p      INTEGER NOT NULL,
            fl_driver  INTEGER NOT NULL,
            pts_s      INTEGER NOT NULL,
            pts_n      INTEGER NOT NULL,
            pts_p      INTEGER NOT NULL,
            timestamp  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_race(race_num, positions, fl_driver, points):
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO races
        (race_num, pos_s, pos_n, pos_p, fl_driver, pts_s, pts_n, pts_p, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (race_num, *positions, fl_driver, *points,
          datetime.now().strftime("%d %b %Y  %H:%M")))
    conn.commit()
    conn.close()

def fetch_all():
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("""SELECT id, race_num, pos_s, pos_n, pos_p,
                        fl_driver, pts_s, pts_n, pts_p, timestamp
                 FROM races ORDER BY race_num ASC""")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_race(race_id):
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("DELETE FROM races WHERE id = ?", (race_id,))
    conn.commit()
    conn.close()

def championship_totals():
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("""SELECT COALESCE(SUM(pts_s),0),
                        COALESCE(SUM(pts_n),0),
                        COALESCE(SUM(pts_p),0)
                 FROM races""")
    row = c.fetchone()
    conn.close()
    return list(row)

def next_race_num():
    conn = sqlite3.connect("f1_championship.db")
    c = conn.cursor()
    c.execute("SELECT COALESCE(MAX(race_num),0)+1 FROM races")
    val = c.fetchone()[0]
    conn.close()
    return val

# ─── App ──────────────────────────────────────────────────────────────────────
class F1App(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("F1 Championship Tracker")
        self.geometry("1000x750")
        self.minsize(860, 600)
        self.configure(bg=F1_DARK)
        self.resizable(True, True)
        self._row_ids = {}
        self._build_ui()
        self.refresh()

    # ── Header ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._header()
        self._championship_table()
        self._input_panel()
        self._race_log()

    def _header(self):
        h = tk.Frame(self, bg=F1_CARBON, height=58)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Frame(h, bg=F1_RED, width=6).pack(side="left", fill="y")
        inner = tk.Frame(h, bg=F1_CARBON)
        inner.pack(side="left", fill="both", expand=True, padx=18, pady=10)
        tk.Label(inner, text="F1  CHAMPIONSHIP  TRACKER",
                 font=("Courier New", 17, "bold"),
                 bg=F1_CARBON, fg=F1_WHITE).pack(side="left")
        tk.Label(inner, text="⚡  FASTEST LAP INCLUDED",
                 font=("Courier New", 9),
                 bg=F1_CARBON, fg="#FFD700").pack(side="right", padx=6)

    # ── Championship standings table (top section) ───────────────────────────
    def _championship_table(self):
        outer = tk.Frame(self, bg=F1_PANEL)
        outer.pack(fill="x")
        tk.Frame(outer, bg=F1_RED, height=2).pack(fill="x")

        title_row = tk.Frame(outer, bg=F1_PANEL)
        title_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(title_row, text="DRIVERS  CHAMPIONSHIP",
                 font=("Courier New", 9, "bold"),
                 bg=F1_PANEL, fg=F1_SILVER).pack(side="left")

        self.champ_frame = tk.Frame(outer, bg=F1_PANEL)
        self.champ_frame.pack(fill="x", padx=20, pady=(0, 12))

        # Placeholder rows (rebuilt on refresh)
        self.champ_rows = []
        for i in range(3):
            row = self._make_champ_row(self.champ_frame, i, DRIVERS[i], 0, 0, DRIVER_COLORS[i], DRIVER_BG[i])
            self.champ_rows.append(row)

        tk.Frame(outer, bg=F1_BORDER, height=1).pack(fill="x")

    def _make_champ_row(self, parent, rank, name, pts, races, color, bg):
        medals = ["🥇", "🥈", "🥉"]
        frame = tk.Frame(parent, bg=bg,
                         highlightbackground=color, highlightthickness=1)
        frame.pack(fill="x", pady=(0, 6))

        # Position badge
        badge = tk.Frame(frame, bg=color, width=44)
        badge.pack(side="left", fill="y")
        badge.pack_propagate(False)
        tk.Label(badge, text=f"P{rank+1}",
                 font=("Courier New", 13, "bold"),
                 bg=color, fg=F1_WHITE).pack(expand=True)

        # Medal + name
        info = tk.Frame(frame, bg=bg, padx=14)
        info.pack(side="left", fill="y", pady=6)
        tk.Label(info, text=f"{medals[rank]}  {name}",
                 font=("Courier New", 13, "bold"),
                 bg=bg, fg=color).pack(anchor="w")
        tk.Label(info, text=f"{races} races",
                 font=("Courier New", 8),
                 bg=bg, fg=F1_SILVER).pack(anchor="w")

        # Points — right side
        pts_frame = tk.Frame(frame, bg=bg)
        pts_frame.pack(side="right", padx=20, pady=6)
        pts_lbl = tk.Label(pts_frame, text=f"{pts}",
                           font=("Courier New", 26, "bold"),
                           bg=bg, fg=F1_WHITE)
        pts_lbl.pack(anchor="e")
        tk.Label(pts_frame, text="PTS",
                 font=("Courier New", 7, "bold"),
                 bg=bg, fg=F1_SILVER).pack(anchor="e")

        return frame

    # ── Input panel ──────────────────────────────────────────────────────────
    def _input_panel(self):
        panel = tk.Frame(self, bg=F1_CARBON)
        panel.pack(fill="x")

        row = tk.Frame(panel, bg=F1_CARBON)
        row.pack(fill="x", padx=20, pady=12)

        tk.Label(row, text="LOG RACE  —  ENTER FINISHING POSITIONS",
                 font=("Courier New", 9, "bold"),
                 bg=F1_CARBON, fg=F1_SILVER).pack(anchor="w")

        fields_row = tk.Frame(panel, bg=F1_CARBON)
        fields_row.pack(fill="x", padx=20, pady=(0, 12))

        vcmd = (self.register(self._val_int), "%P")
        self.pos_vars = []
        self.preview_lbls = []
        self.fl_var = tk.IntVar(value=-1)   # -1 = none selected

        for i, name in enumerate(DRIVERS):
            col = tk.Frame(fields_row, bg=F1_CARBON)
            col.pack(side="left", padx=(0, 24))

            tk.Label(col, text=name.upper(),
                     font=("Courier New", 9, "bold"),
                     bg=F1_CARBON, fg=DRIVER_COLORS[i]).pack(anchor="w")

            erow = tk.Frame(col, bg=F1_CARBON)
            erow.pack(anchor="w")

            var = tk.StringVar()
            self.pos_vars.append(var)

            e = tk.Entry(erow, textvariable=var,
                         font=("Courier New", 15, "bold"),
                         width=4, justify="center",
                         bg=F1_BORDER, fg=F1_WHITE,
                         insertbackground=DRIVER_COLORS[i],
                         relief="flat", bd=0,
                         validate="key", validatecommand=vcmd)
            e.pack(side="left", ipady=7)
            e.bind("<Return>", lambda ev: self._submit())

            prev = tk.Label(erow, text="  —",
                            font=("Courier New", 10, "bold"),
                            bg=F1_CARBON, fg=F1_SILVER)
            prev.pack(side="left", padx=(6, 0))
            self.preview_lbls.append(prev)
            var.trace_add("write", lambda *_, idx=i: self._preview(idx))

            # Fastest lap radio
            tk.Radiobutton(col, text="⚡ Fastest Lap",
                           variable=self.fl_var, value=i,
                           font=("Courier New", 8),
                           bg=F1_CARBON, fg=F1_GOLD,
                           selectcolor=F1_BORDER,
                           activebackground=F1_CARBON,
                           relief="flat", bd=0).pack(anchor="w", pady=(4, 0))

        # Buttons
        btn_col = tk.Frame(fields_row, bg=F1_CARBON)
        btn_col.pack(side="left", anchor="s", padx=(8, 0), pady=(0, 4))

        tk.Button(btn_col, text="▶  LOG RACE",
                  font=("Courier New", 10, "bold"),
                  bg=F1_RED, fg=F1_WHITE,
                  activebackground="#C0001F", activeforeground=F1_WHITE,
                  relief="flat", bd=0, padx=16, pady=8,
                  cursor="hand2", command=self._submit).pack(side="left")

        tk.Button(btn_col, text="✕  DELETE SELECTED",
                  font=("Courier New", 10, "bold"),
                  bg=F1_BORDER, fg=F1_SILVER,
                  activebackground="#3A3A3A", activeforeground=F1_WHITE,
                  relief="flat", bd=0, padx=12, pady=8,
                  cursor="hand2", command=self._delete_selected).pack(side="left", padx=(8, 0))

        tk.Frame(panel, bg=F1_RED, height=2).pack(fill="x")

    # ── Race log table (bottom) ───────────────────────────────────────────────
    def _race_log(self):
        outer = tk.Frame(self, bg=F1_DARK)
        outer.pack(fill="both", expand=True, padx=20, pady=12)

        tk.Label(outer, text="RACE  LOG",
                 font=("Courier New", 8, "bold"),
                 bg=F1_DARK, fg=F1_SILVER).pack(anchor="w", pady=(0, 4))

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("F1.Treeview",
            background=F1_PANEL, foreground=F1_WHITE,
            fieldbackground=F1_PANEL, rowheight=28,
            font=("Courier New", 10), borderwidth=0)
        style.configure("F1.Treeview.Heading",
            background=F1_CARBON, foreground=F1_RED,
            font=("Courier New", 8, "bold"), relief="flat")
        style.map("F1.Treeview",
            background=[("selected", "#3A0010")],
            foreground=[("selected", F1_WHITE)])
        style.layout("F1.Treeview",
            [("F1.Treeview.treearea", {"sticky": "nswe"})])

        frame = tk.Frame(outer, bg=F1_DARK)
        frame.pack(fill="both", expand=True)

        s, n, p = DRIVERS
        cols = ("race", "pos_s", "pts_s", "pos_n", "pts_n", "pos_p", "pts_p", "fl", "time")
        self.tree = ttk.Treeview(frame, columns=cols,
                                  show="headings", style="F1.Treeview")
        headers = [
            ("race",  "RACE",        55),
            ("pos_s", f"{s} POS",   100),
            ("pts_s", f"{s} PTS",    90),
            ("pos_n", f"{n} POS",   100),
            ("pts_n", f"{n} PTS",    90),
            ("pos_p", f"{p} POS",   100),
            ("pts_p", f"{p} PTS",    90),
            ("fl",    "⚡ FL",        80),
            ("time",  "DATE",        160),
        ]
        for col, text, width in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.column("time", anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Logic ────────────────────────────────────────────────────────────────
    def _val_int(self, val):
        return val == "" or (val.isdigit() and int(val) <= 20)

    def _preview(self, idx):
        val = self.pos_vars[idx].get()
        if val.isdigit() and 1 <= int(val) <= 20:
            pts = F1_POINTS[int(val)]
            self.preview_lbls[idx].config(
                text=f"  {pts}pts",
                fg=F1_GOLD if pts > 0 else "#555")
        else:
            self.preview_lbls[idx].config(text="  —", fg=F1_SILVER)

    def _submit(self):
        positions, points = [], []
        for i, var in enumerate(self.pos_vars):
            val = var.get().strip()
            if not val or not val.isdigit() or not (1 <= int(val) <= 20):
                messagebox.showwarning("Missing Input",
                    f"Enter a valid position (1–20) for {DRIVERS[i]}.")
                return
            p = int(val)
            positions.append(p)
            points.append(F1_POINTS[p])

        fl = self.fl_var.get()
        if fl in (0, 1, 2):
            # Only award FL bonus if driver finished in top 10
            if positions[fl] <= 10:
                points[fl] += 1
            else:
                messagebox.showwarning("Fastest Lap",
                    f"{DRIVERS[fl]} must finish in the top 10 to earn the fastest lap point.\nBonus not awarded.")

        insert_race(next_race_num(), positions, fl, points)

        for var in self.pos_vars:
            var.set("")
        for lbl in self.preview_lbls:
            lbl.config(text="  —", fg=F1_SILVER)
        self.fl_var.set(-1)
        self.refresh()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Nothing selected", "Select a race row to delete.")
            return
        for item in sel:
            rid = self._row_ids.get(item)
            if rid:
                delete_race(rid)
        self.refresh()

    def refresh(self):
        # ── Rebuild race log ─────────────────────────────────────────────────
        self._row_ids.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = fetch_all()
        for r in rows:
            rid, rnum, ps, pn, pp, fl_d, pts_s, pts_n, pts_p, ts = r
            fl_name = DRIVERS[fl_d] if fl_d in (0, 1, 2) else "—"
            iid = self.tree.insert("", "end", values=(
                f"R{rnum}",
                f"P{ps}", pts_s,
                f"P{pn}", pts_n,
                f"P{pp}", pts_p,
                fl_name,
                ts
            ))
            self._row_ids[iid] = rid

        # ── Rebuild championship standings ───────────────────────────────────
        totals = championship_totals()   # [pts_s, pts_n, pts_p]
        race_count = len(rows)

        # Sort by points descending
        ranked = sorted(range(3), key=lambda i: -totals[i])

        # Clear old rows
        for w in self.champ_frame.winfo_children():
            w.destroy()
        self.champ_rows = []

        for rank, i in enumerate(ranked):
            name  = DRIVERS[i]
            pts   = totals[i]
            color = DRIVER_COLORS[i]
            bg    = DRIVER_BG[i]
            medals = ["🥇", "🥈", "🥉"]

            frame = tk.Frame(self.champ_frame, bg=bg,
                             highlightbackground=color, highlightthickness=1)
            frame.pack(fill="x", pady=(0, 5))

            # Position badge
            badge = tk.Frame(frame, bg=color, width=46)
            badge.pack(side="left", fill="y")
            badge.pack_propagate(False)
            tk.Label(badge, text=f"P{rank+1}",
                     font=("Courier New", 13, "bold"),
                     bg=color, fg=F1_WHITE).pack(expand=True)

            # Name + races
            info = tk.Frame(frame, bg=bg, padx=14)
            info.pack(side="left", fill="y", pady=5)
            tk.Label(info, text=f"{medals[rank]}  {name}",
                     font=("Courier New", 13, "bold"),
                     bg=bg, fg=color).pack(anchor="w")

            gap_text = f"{race_count} races"
            if rank > 0:
                leader_pts = totals[ranked[0]]
                gap_text += f"   Δ -{leader_pts - pts} pts to leader"
            tk.Label(info, text=gap_text,
                     font=("Courier New", 8),
                     bg=bg, fg=F1_SILVER).pack(anchor="w")

            # Points
            pts_frame = tk.Frame(frame, bg=bg)
            pts_frame.pack(side="right", padx=22, pady=5)
            tk.Label(pts_frame, text=str(pts),
                     font=("Courier New", 26, "bold"),
                     bg=bg, fg=F1_WHITE).pack(anchor="e")
            tk.Label(pts_frame, text="PTS",
                     font=("Courier New", 7, "bold"),
                     bg=bg, fg=F1_SILVER).pack(anchor="e")

            self.champ_rows.append(frame)


if __name__ == "__main__":
    app = F1App()
    app.mainloop()
