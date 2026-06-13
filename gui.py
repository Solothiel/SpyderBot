import customtkinter as ctk


class CrawlerGUI(ctk.CTk):
    def __init__(self, start_crawl_callback):
        super().__init__()
        self.start_crawl_callback = start_crawl_callback

        self.title("Python Web Crawler")
        self.geometry("600x500")
        self.resizable(False, False)

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="Enter Target URL:", font=("Arial", 16))
        self.url_label.pack(pady=(30, 10))

        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="https://example.com")
        self.url_entry.pack(pady=(0, 20))

        # Start Button
        self.start_button = ctk.CTkButton(self, text="Start Crawling", command=self.on_start_click)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        # Log/Status Box
        self.log_textbox = ctk.CTkTextbox(self, width=500, height=200)
        self.log_textbox.pack(pady=10)
        self.log_textbox.configure(state="disabled")

    def on_start_click(self):
        url = self.url_entry.get().strip()
        if url:
            self.start_crawl_callback(url)
            self.start_button.configure(state="disabled")
            self.progress_bar.set(0.1)

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def update_progress(self, value):
        self.progress_bar.set(value)

    def reset_ui(self):
        self.start_button.configure(state="normal")
        self.progress_bar.set(1.0)