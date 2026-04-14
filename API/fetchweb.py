import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import json

# # Suppress SSL warning (common in corporate proxy environments)
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# class WikipediaScraper:
#     """Scrapes links and tables from a Wikipedia page."""

#     HEADERS = {
#         'User-Agent': 'MyLearningScript/1.0 (learning project; contact: your-email@example.com)'
#     }

#     def __init__(self, url):
#         self.url = url
#         self.html_content = None
#         self.soup = None

#     def fetch(self):
#         """Fetch and parse the page HTML."""
#         response = requests.get(self.url, headers=self.HEADERS, verify=False)
#         response.raise_for_status()
#         self.html_content = response.text
#         self.soup = BeautifulSoup(self.html_content, 'html.parser')

#     def get_links(self):
#         """Return a list of (text, href) tuples for all anchor tags."""
#         if self.soup is None:
#             raise RuntimeError("Call fetch() first.")
#         return [
#             (a.get_text(strip=True), a.get('href', ''))
#             for a in self.soup.find_all('a')
#             if a.get_text(strip=True)
#         ]

#     def get_tables(self):
#         """Return a list of DataFrames parsed from all HTML tables."""
#         if self.html_content is None:
#             raise RuntimeError("Call fetch() first.")
#         return pd.read_html(self.html_content)


# if __name__ == '__main__':
#     scraper = WikipediaScraper('https://en.wikipedia.org/wiki/IBM')
#     scraper.fetch()

#     # --- Links ---
#     links = scraper.get_links()
#     print(f"Found {len(links)} links. First 10:")
#     for text, href in links[:10]:
#         print(f"  {text!r:40} -> {href}")

#     # --- Tables ---
#     tables = scraper.get_tables()
#     print(f"\nFound {len(tables)} tables. First table:")
#     print(tables[0].head())



data = requests.get("https://web.archive.org/web/20240929211114/https://fruityvice.com/api/fruit/all")
results = json.loads(data.text)
df2 = pd.json_normalize(pd.DataFrame(results))
cherry = df2.loc[df2["name"] == 'Cherry']
(cherry.iloc[0]['family']) , (cherry.iloc[0]['genus'])
cal_banana = df2.loc[df2["name"]=='Banana']
print(cal_banana.iloc[0]['nutritions.calories'])