import threading
import tkinter as tk
import ttkbootstrap as tb
from gui import CrawlerGUI
from crawler import WebCrawler


class CrawlerApp:
    def __init__(self, root):
        self.root = root
        self.gui = CrawlerGUI(self.root, self.start_crawl_thread)

    def start_crawl_thread(self):
        target_url = self.gui.url_entry.get().strip()
        try:
            max_depth = int(self.gui.depth_spinbox.get())
        except ValueError:
            self.gui.log("[SYSTEM ERROR] Depth entry field values must be valid integer counts.")
            return

        if not target_url.startswith(("http://", "https://")):
            self.gui.log("[SYSTEM ERROR] Target address missing structural HTTP headers protocol prefixes.")
            return

        self.gui.start_button.config(state=tk.DISABLED)
        self.gui.log(
            f"[SYS_INIT] Running targeted domain mapping on: {target_url} up to depth boundary max level: {max_depth}")

        crawl_thread = threading.Thread(target=self.run_crawler, args=(target_url, max_depth), daemon=True)
        crawl_thread.start()

    def run_crawler(self, start_url, max_depth):
        crawler = WebCrawler(start_url, max_depth)
        queue = [(start_url, 0)]
        crawler.visited.add(start_url)

        total_discovered = 1
        processed_count = 0

        self.gui.log(f"[STORAGE DIRECTORY] Files will dump to: {crawler.download_dir}\n")

        while queue:
            current_url, current_depth = queue.pop(0)
            processed_count += 1

            # Step A: Identify if URL is a direct file download link
            if crawler.is_file_url(current_url):
                self.gui.log(f"[Scraping Matrix T-{current_depth}] Extracting File Stream...")
                crawler.download_file(current_url, self.gui.log)
                self.gui.update_progress(processed_count, total_discovered)
                continue

            # Step B: Standard webpage HTML link extraction parsing loop
            self.gui.log(f"[Scraping Matrix T-{current_depth}] Extracting HTML Page: {current_url}")
            self.gui.update_progress(processed_count, total_discovered)

            if current_depth >= max_depth:
                continue

            new_links = crawler.get_links(current_url)
            for link in new_links:
                if link not in crawler.visited:
                    crawler.visited.add(link)
                    queue.append((link, current_depth + 1))
                    total_discovered += 1

                    if crawler.is_file_url(link):
                        self.gui.log(f"   + 📄 [Found File Asset]: {link}")
                    else:
                        self.gui.log(f"   + [Found Web Link]: {link}")

        self.gui.update_progress(processed_count, total_discovered)
        self.gui.status_label.config(text=f"Task ended. Found {len(crawler.visited)} domain nodes mapped successfully.")
        self.gui.log("\n[PROCESS COMPLETE] Engine operational tracking safely shutdown.")
        self.gui.start_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tb.Window(themename="vapor")
    app = CrawlerApp(root)
    root.mainloop()

