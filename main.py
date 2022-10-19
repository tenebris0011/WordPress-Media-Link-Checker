import requests
import logging
import csv

"""
Setup our logging format.
Log file set to ./logs/asset_checker.log
"""
getDate = datetime.now().strftime("%m/%d/%y")
FORMAT = '(%(threadName)-10s) %(message)s'
logging.basicConfig(filename=f'./asset_checker.log', level=logging.INFO, format=FORMAT)

class WebScraper:
    def __init__(self, w):
        self.website = w
        self.post_data = ''
        self.posts_pages = 0
        self.pages_pages = 0
        self.media_pages = 0
        self.bad_media = []
        self.headers = {
            "authority": w,
            "referer": w,
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9,tr;q=0.8",
        }


    def set_site(self, w):
        self.website = w

    def get_media(self):
        for i in range(self.media_pages):
            self.post_data = requests.get(
                self.website + "/wp-json/wp/v2/media?page=" + str(i + 1), headers=self.headers
            ).json()
            for data in self.post_data:
                try:
                    for size in data['media_details']['sizes']:
                        target_url = data['media_details']['sizes'][size]['source_url']
                        logging.info(target_url)
                        response = requests.get(target_url, headers=self.headers)
                        if response.status_code != 200:
                            self.bad_media.append([data['link'], target_url, response.status_code])
                except KeyError:
                    logging.info('KeyError while looking for media_details, checking for source_url instead.')
                    target_url = data['source_url']
                    logging.info(target_url)
                    response = requests.get(target_url, headers=self.headers)
                    if response.status_code != 200:
                        self.bad_media.append([data['link'], target_url, response.status_code])

    def get_site_info(self):
        logging.info(f"Starting on site {self.website}")
        self.media_pages = int(requests.get(self.website + "/wp-json/wp/v2/media", headers=self.headers).headers["X-WP-TotalPages"])
        total_media = int(requests.get(self.website + "/wp-json/wp/v2/media", headers=self.headers).headers["X-WP-Total"])
        logging.info(f"{total_media} media links to scan for {self.website}")


    def get_bad_media(self):
        return self.bad_media

def csv_creator(data):
    with open(f"./results.csv", 'w') as f:
        header_row = ["Found On", "Bad Asset", "Status Code"]
        write = csv.writer(f)
        write.writerow(header_row)
        for item in data:
            write.writerow(item)



found_bad_items = []

with open('./resources/sites.txt', 'r') as f:
    sites = f.readlines()
    scraper = WebScraper('')
    for site in sites:
        scraper.set_site(site.strip())
        scraper.get_site_info()
        scraper.get_media()
        found_bad_items.extend(scraper.get_bad_media())

"""
scraper = WebScraper('https://www.drkanumilliny.com/')
scraper.get_site_info()
scraper.get_posts_pages_media()
found_bad_items.extend(scraper.get_bad_media())
"""
if len(found_bad_items) > 0:
    csv_creator(found_bad_items)
else:
    logging.info("No bad media items found.")
