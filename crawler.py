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

    def clean_and_normalize_url(self, base_url, href_target):
        """
        Forces structural validation on raw anchors to cleanly prevent 
        duplicate schemes or corrupt inline relative path loops.
        """
        href_target = href_target.strip()

        # 1. Catch anchors that already contain a valid absolute web structure
        if href_target.startswith(("http://", "https://")):
            return href_target

        # 2. Prevent string corruption if an absolute path is missing its protocol prefix
        if href_target.startswith("//"):
            base_scheme = urllib.parse.urlparse(base_url).scheme
            return f"{base_scheme or 'https'}:{href_target}"

        # 3. Clean out dangerous prefix steps inside messy subfolder paths
        href_target = re.sub(r'^(?:\.?\.?/)+', '', href_target)

        # 4. Safely fall back to manual string combining if standard urljoin breaks down
        parsed_base = urllib.parse.urlparse(base_url)
        base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"

        if href_target.startswith("/"):
            return f"{base_origin}{href_target}"

        # Standard structural directory fallback
        base_path = parsed_base.path
        if not base_path.endswith("/"):
            base_path = os.path.dirname(base_path).replace("\\", "/")
            if not base_path.endswith("/"):
                base_path += "/"

        return f"{base_origin}{base_path}{href_target}"

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

            is_attachment = "attachment" in content_disposition.lower()
            is_not_html = "text/html" not in content_type

            if is_attachment or is_not_html:
                log_callback(f"   [File Detected] Processing stream layout...")
                return self.download_file(url, content_disposition, log_callback), set()

            # Execute a standard GET request to scrape links from HTML pages
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return False, set()

            links = set()
            soup = BeautifulSoup(response.text, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                raw_href = anchor['href']

                # Skip raw programmatic commands or empty targets
                if raw_href.startswith(("javascript:", "mailto:", "tel:", "#")) or not raw_href.strip():
                    continue

                # Run through the custom normalization engine
                absolute_url = self.clean_and_normalize_url(url, raw_href)

                # Safe structure parsing
                parsed_url = urllib.parse.urlparse(absolute_url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"

                # Ensure the spider stays on the base target domain
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

            if content_disposition:
                match = re.search(r'filename=["\']?([^"\']+)', content_disposition)
                if match:
                    filename = match.group(1)

            if not filename:
                parsed_path = urllib.parse.urlparse(url).path
                filename = os.path.basename(parsed_path)

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
