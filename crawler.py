import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

''' creates a class (blueprint for creating object) and then initializes 
    an instance variable to keep track of visited URLs
'''

class WebCrawler:
    def __init__(self):
        self.visited_urls = set()


    """ This uses urlparse to split the URL into components, then ensures 
    the crawler follows link on the target domain, ignores external sites,
    ignores non-web links and ignores relative urls that aren't converted
    """
    def is_valid_url(self, url, base_domain):
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == base_domain and parsed.scheme in ("http", "https")

    """ This is the webcrawler → it starts crawling on the given url.
        The greats an empty list to store data. Then it creates a queue
        containing the first URL to vist. This also helps prevents from revisting
        the same page, while presenting as a browser running on windows"""
    def crawl(self, start_url):
        results = []
        queue = [start_url]
        base_domain = urlparse(start_url).netloc
        self.visited_urls.add(start_url)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64"}


        ''' removes and returns the first url in the queue, then sends updates as it 
        crawls '''
        while queue:
            current_url = queue.pop(0)
            yield {'type': 'status', 'message': f'Crawling: {current_url}'}

            try:
                '''Makes a requests, waits at most 5 seconds, then  if it succeeds, 
                    adds the crawled page to the results list'''

                response = requests.get(current_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    results.append(current_url)
                    soup = BeautifulSoup(response.content, "html.parser")

                    for a_tag in soup.find_all('a', href=True):
                        full_url = urljoin(current_url, a_tag['href'])
                        full_url = full_url.split('#')[0]


                        if full_url not in self.visited_urls and self.is_valid_url(full_url, base_domain):
                            self.visited_urls.add(full_url)
                            queue.append(full_url)
                            yield {'type': 'found', 'url': full_url}


                '''Catches any problem such as connection failures, timeout, invalid urls,
                    DNS errors and reports the error'''

            except Exception as e:
                yield {'type': 'error', 'message': f'failed {current_url}: {str(e)}'}
                continue

        yield   {'type': 'finished', 'urls': results}   #reports when crawler is done.



