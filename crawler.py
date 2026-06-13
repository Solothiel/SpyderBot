import os
import urllib.parse
import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, base_url, max_depth):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()

        # Define file types you want to automatically download
        self.file_extensions = (
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.csv'
        )

        # Target path: User's system Downloads folder / Spyderbot_treasure
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Spyderbot_treasure")
        os.makedirs(self.download_dir, exist_ok=True)

    def is_file_url(self, url):
        """Checks if the clean path of the URL ends with a target file extension."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        return path.endswith(self.file_extensions)

    def download_file(self, url, log_callback):
        """Downloads the file securely to the local treasure folder."""
        try:
            parsed = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed.path)

            # Fallback if filename cannot be cleanly parsed from the URL
            if not filename:
                filename = "downloaded_asset_" + str(hash(url))

            local_filepath = os.path.join(self.download_dir, filename)

            # Download file using stream to handle larger files efficiently
            with requests.get(url, stream=True, timeout=10) as response:
                if response.status_code == 200:
                    with open(local_filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    log_callback(f"   📥 [DOWNLOADED] -> {filename}")
                    return True
        except Exception as e:
            log_callback(f"   ❌ [DOWNLOAD ERROR] -> Failed to grab file: {str(e)}")
        return False

    def get_links(self, url):
        """Fetches HTML pages and parses links while skipping file URLs."""
        links = set()

        # If the URL itself is a file, we do not parse it for HTML elements
        if self.is_file_url(url):
            return links

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                return links

            soup = BeautifulSoup(response.text, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                absolute_url = urllib.parse.urljoin(url, href)

                parsed_url = urllib.parse.urlparse(absolute_url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

                if urllib.parse.urlparse(self.base_url).netloc == parsed_url.netloc:
                    links.add(clean_url)
        except Exception:
            pass
