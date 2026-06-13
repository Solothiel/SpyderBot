import os
import sys
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.widgets import Scrolled
from PIL import Image, ImageTk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CrawlerGUI:
    def __init__(self, root, start_callback):
        self.root = root
        self.root.title("Spider Crawler Pro")
        self.root.geometry("750x600")
        self.root.minsize(700, 550)
        self.start_callback = start_callback
        self.create_widgets()

    def create_widgets(self):
        header_frame = tb.Frame(self.root, bootstyle="secondary", padding=10)
        header_frame.pack(fill=tk.X)

        try:
            logo_img_path = resource_path("logo.png")
            opened_logo = Image.open(logo_img_path)
            resized_logo = opened_logo.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_logo)
            logo_label = tb.Label(header_frame, image=self.logo_image, bootstyle="inverse-secondary")
            logo_label.pack(side=tk.LEFT, padx=(5, 15))
        except Exception:
            pass

        header_title = tb.Label(header_frame, text="WEB SPIDER APP", font=("Courier New", 18, "bold"), bootstyle="inverse-secondary")
        header_title.pack(side=tk.LEFT)

        body_frame = tb.Frame(self.root, padding=20)
        body_frame.pack(fill=tk.BOTH, expand=True)

        config_frame = tb.LabelFrame(body_frame, text=" CONFIGURATION PANEL ", padding=15, bootstyle="info")
        config_frame.pack(fill=tk.X, pady=(0, 15))

        tb.Label(config_frame, text="Target Domain Website:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.url_entry = tb.Entry(config_frame, width=45)
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tb.Label(config_frame, text="Max Scraping Depth Target:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.depth_spinbox = tb.Spinbox(config_frame, from_=1, to=10, width=5)
        self.depth_spinbox.set(2)
        self.depth_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.start_button = tb.Button(config_frame, text="RUN ENGINE", bootstyle="info", command=self.start_callback, width=15)
        self.start_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="nsew")
        config_frame.columnconfigure(1, weight=1)

        self.progress_bar = tb.Progressbar(body_frame, orient="horizontal", mode="determinate", bootstyle="info-striped")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.status_label = tb.Label(body_frame, text="Engine idle. Awaiting configuration input parameters.", font=("Helvetica", 9, "italic"))
        self.status_label.pack(anchor=tk.W, pady=(0, 15))

        self.log_area = ScrolledText(body_frame, wrap=tk.WORD, height=12, autohide=True)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def update_progress(self, current, total):
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_bar['value'] = percentage
        self.status_label.config(text=f"Progress tracking metrics: {current} parsed / {total} discovered nodes mapped.")
        self.root.update_idletasks()
