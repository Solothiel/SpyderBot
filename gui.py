import os
import sys
import tkinter as tk
import ttkbootstrap as tb
from PIL import Image, ImageTk


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


class CrawlerGUI:
    def __init__(self, root, start_callback):
        self.root = root
        self.start_callback = start_callback

        self.root.title("☾ Solothiel's Web Crawler ☽")
        self.root.geometry("750x600")
        self.root.minsize(700, 550)

        self.create_widgets()

    def create_widgets(self):

        # =========================
        # HEADER ( BANNER)
        # =========================
        header_frame = tb.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)

        #  logo (UPDATED)
        try:
            logo_img_path = resource_path("assets/moon_logo.png")
            opened_logo = Image.open(logo_img_path)

            resized_logo = opened_logo.resize((60, 60), Image.LANCZOS)

            self.logo_image = ImageTk.PhotoImage(resized_logo)

            logo_label = tb.Label(
                header_frame,
                image=self.logo_image,
                background="#0A0A0A"
            )
            logo_label.pack(side=tk.LEFT, padx=(5, 15))

        except Exception as e:
            print(f"[LOGO LOAD ERROR] {e}")

        header_title = tb.Label(
            header_frame,
            text="☾ Solothiel's WEB CRAWLER ☽",
            font=("Segoe UI", 16, "bold"),
            foreground="#FFFFFF",
            background="#0A0A0A"
        )
        header_title.pack(side=tk.LEFT)

        # =========================
        # BODY
        # =========================
        body_frame = tb.Frame(self.root, padding=20)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # CONFIG FRAME
        config_frame = tb.Labelframe(
            body_frame,
            text=" CONFIGURATION PANEL ",
            bootstyle="secondary"
        )
        config_frame.pack(fill=tk.X, pady=(0, 15))

        tb.Label(
            config_frame,
            text="Target Domain Website:",
            font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.url_entry = tb.Entry(config_frame, width=45)
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tb.Label(
            config_frame,
            text="Max Scraping Depth:",
            font=("Helvetica", 10, "bold")
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.depth_spinbox = tb.Spinbox(config_frame, from_=1, to=10, width=5)
        self.depth_spinbox.set(2)
        self.depth_spinbox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.start_button = tb.Button(
            config_frame,
            text="☾ RUN ENGINE ☽",
            bootstyle="light",
            command=self.start_callback,
            width=15
        )
        self.start_button.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        config_frame.columnconfigure(1, weight=1)

        # =========================
        # PROGRESS
        # =========================
        self.progress_bar = tb.Progressbar(
            body_frame,
            orient="horizontal",
            mode="determinate",
            bootstyle="secondary"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.status_label = tb.Label(
            body_frame,
            text="Engine idle. Awaiting mission parameters.",
            font=("Helvetica", 9, "italic")
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 15))

        # =========================
        # LOG AREA
        # =========================
        log_container = tb.Frame(body_frame)
        log_container.pack(fill=tk.BOTH, expand=True)

        self.log_area = tb.Text(
            log_container,
            wrap=tk.WORD,
            height=12,
            font=("Consolas", 10)
        )
        self.log_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tb.Scrollbar(
            log_container,
            orient="vertical",
            bootstyle="secondary",
            command=self.log_area.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_area.configure(yscrollcommand=scrollbar.set)

    # =========================
    # LOGGING
    # =========================
    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def update_progress(self, current, total):
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_bar["value"] = percentage

        self.status_label.config(
            text=f"Progress: {current} / {total} nodes mapped"
        )

        self.root.update_idletasks()


if __name__ == "__main__":
    def dummy_callback():
        print("Test run OK")

    root = tb.Window(themename="cyborg")

    app = CrawlerGUI(root, dummy_callback)

    app.log("[SYSTEM] GUI standalone test mode active.")

    root.mainloop()