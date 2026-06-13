import os
import sys
import threading
import tkinter as tk
import ttkbootstrap as tb

from gui import CrawlerGUI
from crawler import WebCrawler


def resource_path(relative_path):
    """
    Returns the correct path to assets whether running
    from source or a PyInstaller executable.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


class CrawlerApp:
    def __init__(self, root):
        self.root = root

        #  logo path
        self.logo_path = resource_path("assets/moon_logo.png")

        self.gui = CrawlerGUI(
            self.root,
            self.start_crawl_thread
        )

    def start_crawl_thread(self):
        target_url = self.gui.url_entry.get().strip()

        try:
            max_depth = int(self.gui.depth_spinbox.get())
        except ValueError:
            self.gui.log(
                "[SYSTEM ERROR] Depth entry field values must be valid integer counts."
            )
            return

        if not target_url.startswith(("http://", "https://")):
            self.gui.log(
                "[SYSTEM ERROR] Target address missing structural HTTP headers protocol prefixes."
            )
            return

        self.gui.start_button.config(state=tk.DISABLED)

        self.gui.log(
            f"[SYS_INIT] Running targeted domain mapping on: "
            f"{target_url} up to depth boundary max level: {max_depth}"
        )

        crawl_thread = threading.Thread(
            target=self.run_crawler,
            args=(target_url, max_depth),
            daemon=True
        )

        crawl_thread.start()

    def run_crawler(self, start_url, max_depth):
        crawler = WebCrawler(start_url, max_depth)

        queue = [(start_url, 0)]
        crawler.visited.add(start_url)

        total_discovered = 1
        processed_count = 0

        self.gui.log(
            f"[STORAGE DIRECTORY] Live Target Path: {crawler.download_dir}\n"
        )

        while queue:
            current_url, current_depth = queue.pop(0)

            processed_count += 1

            self.gui.log(
                f"[Analyzing Node T-{current_depth}] -> {current_url}"
            )

            self.gui.update_progress(
                processed_count,
                total_discovered
            )

            success, discovered_links = crawler.process_url(
                current_url,
                self.gui.log
            )

            if current_depth >= max_depth:
                continue

            if success and discovered_links is not None:
                for link in discovered_links:
                    if link not in crawler.visited:
                        crawler.visited.add(link)

                        queue.append(
                            (
                                link,
                                current_depth + 1
                            )
                        )

                        total_discovered += 1

                        self.gui.log(
                            f"   + [Discovered Node]: {link}"
                        )

        self.gui.update_progress(
            processed_count,
            total_discovered
        )

        self.gui.status_label.config(
            text="Task ended. Engine processed all discovered nodes."
        )

        self.gui.log(
            "\n[PROCESS COMPLETE] Engine operational tracking safely shutdown."
        )

        self.gui.start_button.config(
            state=tk.NORMAL
        )


if __name__ == "__main__":

    root = tb.Window(
        themename="cyborg"
    )

    root.title(
        "☾ Solothiel's Web Crawler ☽"
    )

    root.geometry(
        "1200x800"
    )

    root.minsize(
        1000,
        700
    )

    style = tb.Style()

    # colors
    root.configure(
        bg="#0A0A0A"
    )

    style.configure(
        "Moon.TFrame",
        background="#0A0A0A"
    )

    style.configure(
        "Moon.TLabel",
        background="#0A0A0A",
        foreground="#F2F2F2"
    )

    style.configure(
        "MoonTitle.TLabel",
        background="#0A0A0A",
        foreground="#FFFFFF",
        font=("Segoe UI", 18, "bold")
    )

    style.configure(
        "Moon.TButton",
        foreground="#000000"
    )

    app = CrawlerApp(root)

    root.mainloop()