import os
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup


class WebCrawler:
    def __init__(self, base_url, max_depth):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()

        # Target path: User's system Downloads folder / Spyderbot_treasure
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Spyderbot_treasure")
        os.makedirs(self.download_dir, exist_ok=True)

    def process_url(self, url, log_callback):
        """
        Inspects live headers of a URL to determine if it is a downloadable file
        or an HTML webpage, processing it appropriately.
        """
        try:
            # Send a HEAD request first to inspect the content type without wasting bandwidth downloading
            header_response = requests.head(url, allow_redirects=True, timeout=5)
            content_type = header_response.headers.get("Content-Type", "").lower()
            content_disposition = header_response.headers.get("Content-Disposition", "")

            # 1. Check if the server explicitly tells us this is an attachment/file download
            is_attachment = "attachment" in content_disposition.lower()
            is_not_html = "text/html" not in content_type

            if is_attachment or is_not_html:
                log_callback(f"[File Detected] Processing stream layout...")
                return self.download_file(url, content_disposition, log_callback), set()

            # 2. If it is an HTML webpage, execute a standard GET request to scrape links
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return False, set()

            links = set()
            soup = BeautifulSoup(response.text, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                absolute_url = urllib.parse.urljoin(url, href)

                parsed_url = urllib.parse.urlparse(absolute_url)
                # Keep tracking queries/parameters since file databases rely on them
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"

                # Stay on the base domain
                if urllib.parse.urlparse(self.base_url).netloc == parsed_url.netloc:
                    links.add(clean_url)

            return True, links

        except Exception as e:
            log_callback(f"   ❌ [ERR] Connect failed on path: {str(e)}")
            return False, set()

    def download_file(self, url, content_disposition, log_callback):
        """Downloads the file by safely generating filenames from headers or paths."""
        try:
            filename = None

            # Extract filename from Content-Disposition header if available
            if content_disposition:
                match = re.search(r'filename=["\']?([^"\']+)', content_disposition)
                if match:
                    filename = match.group(1)

            # Fallback to extracting from the URL path if header extraction fails
            if not filename:
                parsed_path = urllib.parse.urlparse(url).path
                filename = os.path.basename(parsed_path)

            # Strict Fallback if it's a completely blind query script string
            if not filename or filename.strip() in ("", "/"):
                filename = f"asset_{abs(hash(url))}.dat"

            # Clean forbidden operating system characters from filename
            filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
            local_filepath = os.path.join(self.download_dir, filename)

            # Stream download bytes array
            with requests.get(url, stream=True, timeout=15) as response:
                if response.status_code == 200:
                    with open(local_filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    log_callback(f"   📥 [DOWNLOADED] -> {filename}")
                    return True
        except Exception as e:
            log_callback(f"   ❌ [DOWNLOAD ERROR] -> {str(e)}")
        return False
