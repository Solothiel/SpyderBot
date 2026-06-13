import threading
from gui import CrawlerGUI
from crawler import WebCrawler

class MainApp:
    def __init__(self):
        self.gui = CrawlerGUI(self.start_crawling)
        self.crawler = WebCrawler()


    def run_crawler_thread(self, start_url):
        for data in self.crawler.crawl(start_url):
            if data['type'] == 'status' or data['type'] == 'error':
                self.gui.log(data['message'])
            elif data['type'] == 'found':
                self.gui.log(f"Found: {data['url']}")
            elif data['type'] == 'finished':
                self.gui.log(f"--- Crawl Finished! Total URLs: {len(data['urls'])} ---")
                self.gui.reset_ui()


    def start_crawling(self, start_url):
        self.gui.log(f"Starting crawl at {start_url}...")
        # Run in a separate thread so the GUI does not freeze
        thread = threading.Thread(target=self.run_crawler_thread, args=(start_url,))
        thread.daemon = True
        thread.start()

    def start(self):
        self.gui.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.start()
