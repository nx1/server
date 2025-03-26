import os
import requests

class Discogs:
    def __init__(self, **kwargs):
        self.token = os.getenv("DISCOGS_TOKEN")
        self.response = None

    @property
    def headers(self):
        headers = {"User-Agent": "DiscogsAPI/1.0"}
        return headers

    def search(self, **kwargs):
        base_url = 'https://api.discogs.com/database/search'

        pagination = {'page': 1,
                      'per_page': 100}

        params = {"token": self.token,
                  **pagination,
                  **kwargs}
        self.response = requests.get(base_url,
                                     headers=self.headers,
                                     params=params)

    @property
    def json(self):
        return self.response.json()

if __name__ == "__main__":
    d = Discogs()
    d.search(
       style="Psy-Trance,Progressive Trance",
       format="Compilation",
       year="2000-2009",
       sort="have",
       sort_order="desc",
       )
    print(d.response)
    print(d.json)
