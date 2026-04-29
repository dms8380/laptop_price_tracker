"""
gui.py
Dark-themed tkinter GUI for the tracker
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.scraper import scrape_laptops
from scraper.data_manager import get_statistics
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
#Colour palette
BG      = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT  = "#7c3aed"
CYAN    = "#06b6d4"
TEXT    = "#e2e8f0"
MUTED   = "#94a3b8"
GREEN   = "#4ade80"
RED     = "#fca5a5"
BORDER  = "#3a3a5e"

class LaptopTrackerApp(tk.Tk):
    #Main application

    def __init__(self):
        super().__init__()
        self.title("💻 Laptop Price Tracker for laptops on webscraper.io/test-sites/e-commerce/static/computers/laptops")
        self.geometry("1200x720")
        self.minsize(950, 600)
        self.configure(bg=BG)
        # this part the current list of scraped laptops
        self.laptops: list[dict] = []
        self._build_header()
        self._build_controls()
        self._build_status_bar()
        self._build_main_area()

    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=12)
        hdr.pack(fill="x")

        tk.Label(
            hdr, text="💻  Laptop Price Tracker",
            font=("Helvetica", 20, "bold"),
            bg=ACCENT, fg="white"
        ).pack(side="left", padx=20)
        tk.Label(
            hdr, text="Source: webscraper.io  |  Real refurbished laptop data",
            font=("Helvetica", 9), bg=ACCENT, fg="#c4b5fd"
        ).pack(side="right", padx=20)

    #controls
    def _build_controls(self):
        ctrl = tk.Frame(self, bg=SURFACE, pady=10, padx=16)
        ctrl.pack(fill="x")
        # Page spinbox
        tk.Label(
            ctrl, text="Pages to scrape:",
            bg=SURFACE, fg=TEXT, font=("Helvetica", 10)
        ).grid(row=0, column=0, padx=(0, 6))

        self.pages_var = tk.IntVar(value=3)
        tk.Spinbox(
            ctrl, from_=1, to=10,
            textvariable=self.pages_var,
            width=4, font=("Helvetica", 10)
        ).grid(row=0, column=1, padx=(0, 16))

        # Scrape button
        self.scrape_btn = tk.Button(
            ctrl, text="🔍  Scrape Laptops",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg="white", relief="flat",
            padx=20, pady=7,
            command=self._start_scrape
        )
        self.scrape_btn.grid(row=0, column=2, padx=(0, 20))

        tk.Label(
            ctrl,
            text="Fetches live refurbished laptop listings from webscraper.io",
            font=("Helvetica", 9), bg=SURFACE, fg=MUTED
        ).grid(row=0, column=3, sticky="w")


    def _build_status_bar(self):
        self.status_var = tk.StringVar(
            value="Ready — press 'Scrape Laptops' to fetch live data."
        )
        tk.Label(
            self, textvariable=self.status_var,
            bg=SURFACE, fg=MUTED,
            font=("Helvetica", 9), anchor="w", padx=12, pady=3
        ).pack(fill="x")

    #main area
    def _build_main_area(self):
        pane = tk.PanedWindow(self, orient="horizontal",
                              bg=BG, sashwidth=6, sashrelief="flat")
        pane.pack(fill="both", expand=True, padx=8, pady=8)

        #sortable table
        left = tk.Frame(pane, bg=BG)
        pane.add(left, minsize=520)
        self._build_table(left)

        #stats + chart
        right = tk.Frame(pane, bg=BG)
        pane.add(right, minsize=360)
        self._build_stats_panel(right)

        if MATPLOTLIB_OK:
            self._build_chart(right)
        else:
            tk.Label(
                right,
                text="📦  Install matplotlib to see the price chart:\n\npip install matplotlib",
                bg=BG, fg=MUTED, font=("Helvetica", 10), justify="center"
            ).pack(pady=30)

    #main table
    def _build_table(self, parent):
        tk.Label(
            parent, text="Laptop Listings",
            bg=BG, fg=TEXT, font=("Helvetica", 13, "bold")
        ).pack(anchor="w", pady=(0, 6))
        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=SURFACE, foreground=TEXT,
                        rowheight=28, fieldbackground=SURFACE,
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading",
                        background=ACCENT, foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", CYAN)])

        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True)
        cols = ("Name", "Price", "Rating")
        self.tree = ttk.Treeview(frame, columns=cols,
                                  show="headings", selectmode="browse")

        col_widths = {"Name": 340, "Price": 110, "Rating": 120}
        for col in cols:
            self.tree.heading(
                col, text=col,
                command=lambda c=col: self._sort_column(c)
            )
            self.tree.column(col, width=col_widths[col], anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        #color tags
        self.tree.tag_configure("top",  background="#1e3a2f", foreground=GREEN)
        self.tree.tag_configure("even", background=SURFACE)
        self.tree.tag_configure("odd",  background="#222236")

        tk.Label(
            parent,
            text="💡 Click any column header to sort",
            bg=BG, fg=MUTED, font=("Helvetica", 8)
        ).pack(anchor="w", pady=(4, 0))

    def _populate_table(self):
        #Refresh with current self.laptops data
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, laptop in enumerate(self.laptops):
            # Build star string; show N/A if no rating
            if laptop["rating"] > 0:
                filled = int(laptop["rating"])
                empty  = 5 - filled
                stars  = "★" * filled + "☆" * empty + f"  {laptop['rating']:.1f}"
            else:
                stars = "No rating"
            tag = "top" if laptop["rating"] >= 4.5 else ("even" if i % 2 == 0 else "odd")
            self.tree.insert("", "end", values=(
                laptop["name"],
                laptop["price_str"],
                stars,
            ), tags=(tag,))
    def _sort_column(self, col: str):
        #Sort table by the clicked column
        key_map = {
            "Name":   lambda l: l["name"].lower(),
            "Price":  lambda l: l["price"],
            "Rating": lambda l: l["rating"],
        }
        self.laptops.sort(key=key_map[col])
        self._populate_table()
        self.status_var.set(f"Sorted by {col}.")

    #stats panel
    def _build_stats_panel(self, parent):
        tk.Label(
            parent, text="📊 Summary Statistics",
            bg=BG, fg=TEXT, font=("Helvetica", 13, "bold")
        ).pack(anchor="w", pady=(0, 6))

        sf = tk.Frame(parent, bg=SURFACE, padx=14, pady=12)
        sf.pack(fill="x", padx=4, pady=(0, 12))
        self.stat_labels: dict[str, tk.Label] = {}
        rows = [
            ("total",         "Total Laptops"),
            ("avg_price",     "Avg Price"),
            ("min_price",     "Min Price"),
            ("max_price",     "Max Price"),
            ("avg_rating",    "Avg Rating"),
            ("rated_count",   "Laptops Rated"),
            ("lowest_priced", "Best Value"),
            ("highest_rated", "Top Rated"),
        ]
        for key, label in rows:
            row = tk.Frame(sf, bg=SURFACE)
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=label + ":", bg=SURFACE, fg=MUTED,
                font=("Helvetica", 10), width=15, anchor="w"
            ).pack(side="left")
            lbl = tk.Label(
                row, text="—", bg=SURFACE, fg=CYAN,
                font=("Helvetica", 10, "bold"),
                anchor="w", wraplength=200, justify="left"
            )
            lbl.pack(side="left", fill="x")
            self.stat_labels[key] = lbl

    def _update_stats(self):
        #Recompute and display the summary stats
        s = get_statistics(self.laptops)
        if not s:
            return
        self.stat_labels["total"].config(text=str(s["total"]))
        self.stat_labels["avg_price"].config(text=f"${s['avg_price']:,.2f}")
        self.stat_labels["min_price"].config(text=f"${s['min_price']:,.2f}")
        self.stat_labels["max_price"].config(text=f"${s['max_price']:,.2f}")
        self.stat_labels["avg_rating"].config(
            text=f"{s['avg_rating']:.1f} / 5.0" if s["avg_rating"] > 0 else "N/A"
        )
        self.stat_labels["rated_count"].config(text=str(s["rated_count"]))
        self.stat_labels["lowest_priced"].config(text=s["lowest_priced"])
        self.stat_labels["highest_rated"].config(text=s["highest_rated"])

    #chart
    def _build_chart(self, parent):
        tk.Label(
            parent, text="📈 Price Distribution",
            bg=BG, fg=TEXT, font=("Helvetica", 13, "bold")
        ).pack(anchor="w", pady=(0, 4))

        self.fig = Figure(figsize=(4.2, 3.2), dpi=90, facecolor=SURFACE)
        self.ax  = self.fig.add_subplot(111)
        self.ax.set_facecolor(SURFACE)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4)
        self._draw_empty_chart()
    def _draw_empty_chart(self):
        self.ax.clear()
        self.ax.set_facecolor(SURFACE)
        self.ax.text(
            0.5, 0.5, "No data yet\nPress Scrape to load",
            ha="center", va="center",
            color=MUTED, fontsize=10,
            transform=self.ax.transAxes
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_edgecolor(BORDER)
        self.canvas.draw()

    def _update_chart(self):
        #Redraw the price histogram with updated
        prices = [l["price"] for l in self.laptops]
        self.ax.clear()
        self.ax.set_facecolor(SURFACE)
        self.ax.hist(prices, bins=12, color=ACCENT,
                     edgecolor=BG, linewidth=0.6)
        self.ax.set_title("Price Distribution (USD)", color=MUTED, fontsize=9)
        self.ax.set_xlabel("Price ($)", color=MUTED, fontsize=8)
        self.ax.set_ylabel("# of Laptops", color=MUTED, fontsize=8)
        self.ax.tick_params(colors=MUTED, labelsize=7)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(BORDER)
        self.fig.tight_layout()
        self.canvas.draw()

    #scraping
    def _start_scrape(self):
        #Disable button and launch scraper on background thread
        pages = self.pages_var.get()
        self.scrape_btn.config(state="disabled", text="⏳  Scraping...")
        self.status_var.set(
            "Scraping webscraper.io — please wait..."
        )
        threading.Thread(target=self._do_scrape, args=(pages,), daemon=True).start()
    def _do_scrape(self, pages: int):
        #runs scrape_laptops() then posts UI update
        try:
            laptops = scrape_laptops(max_pages=pages)
            self.laptops = laptops
            self.after(0, self._on_scrape_done)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Scrape Error", str(e)))
            self.after(0, lambda: self.scrape_btn.config(
                state="normal", text="🔍  Scrape Laptops"
            ))

    def _on_scrape_done(self):
        #Called on main once scraping is complete
        count = len(self.laptops)
        self.scrape_btn.config(state="normal", text="🔍  Scrape Laptops")
        if count == 0:
            self.status_var.set(
                "⚠️  No laptops found. The site may have changed its HTML structure."
            )
            messagebox.showwarning(
                "No Data",
                "No laptops were found.\n\n"
                "webscraper.io may have updated its HTML.\n"
                
            )
            return
        self.status_var.set(
            f"✅  Loaded {count} laptops from webscraper.io "
            "Click a column header to sort."
        )
        self._populate_table()
        self._update_stats()
        if MATPLOTLIB_OK:
            self._update_chart()


def launch():
    #Entry point called by main.py
    app = LaptopTrackerApp()
    app.mainloop()
