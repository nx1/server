import os
import time
import requests
from typing import List, Dict, Any

class Discogs:
    def __init__(self, **kwargs):
        self.token = os.getenv("DISCOGS_TOKEN")
        self.headers = {"User-Agent": "DiscogsAPI/1.0"}
    
    def get(self, url, **kwargs):
        params = {"token": self.token, **kwargs}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.text}")

        # check rate limit
        if response.headers.get('x-discogs-ratelimit-remaining') == '0':
            print(f"Rate limit exceeded, sleeping for 60 seconds")
            time.sleep(60)
        return response

    def search(self, **kwargs):
        base_url = 'https://api.discogs.com/database/search'

        pagination = {'page': 1,
                      'per_page': 100}

        params = {"token": self.token,
                  **pagination,
                  **kwargs}
        response = self.get(base_url, params=params)
        return response.json()
    

    def get_artist_releases(self, artist_id, sort='year', sort_order='desc'):
        base_url = f'https://api.discogs.com/artists/{artist_id}/releases'
        
        params = {
            "token": self.token,
            "sort": sort,
            "sort_order": sort_order,
            "per_page": 100
        }
        
        page = 1

        response = self.get(url=base_url, params=params)
        data = response.json()

        total_pages = data['pagination']['pages']
        total_items = data['pagination']['items']
        print(f"Total pages: {total_pages}, Total items: {total_items}")

        all_releases = []
        for page in range(1, total_pages + 1):
            print(f"Getting page {page} / {total_pages}")
            params['page'] = page
            response = self.get(url=base_url, params=params)
            data = response.json()
            all_releases.extend(data['releases'])
            print(f"Got {len(data['releases'])} releases")
        return all_releases

    def get_release_tracks(self, release_id):
        base_url = f'https://api.discogs.com/releases/{release_id}'
        params = {"token": self.token}
        response = self.get(url=base_url, params=params)
        data = response.json()
        return data.get('tracklist', [])

    def get_artist_tracks(self, artist_id):
        print(f"Getting artist tracks for {artist_id}")
        releases = self.get_artist_releases(artist_id)
        all_tracks = []
        print(f"Got {len(releases)} releases")

        for release in releases:
            print(f"Processing release {release['id']}")
            if release.get('type') == 'master':
                continue
                
            tracks = self.get_release_tracks(release['id'])
            for track in tracks:
                if 'artists' in track:
                    # If the track has multiple artists, only include if our artist is one of them
                    if any(artist['id'] == artist_id for artist in track['artists']):
                        all_tracks.append({
                            'title'    : track['title'],
                            'release'  : release['title'],
                            'year'     : release.get('year'),
                            'position' : track.get('position'),
                            'duration' : track.get('duration'),
                            'type'     : track.get('type_')
                        })
                else:
                    all_tracks.append({
                        'title'    : track['title'],
                        'release'  : release['title'],
                        'year'     : release.get('year'),
                        'position' : track.get('position'),
                        'duration' : track.get('duration'),
                        'type'     : track.get('type_')
                    })
        print(f"Got {len(all_tracks)} tracks")
        return all_tracks

    def get_label_releases(self, label_id):
        print(f"Getting label releases for {label_id}")
        base_url = f'https://api.discogs.com/labels/{label_id}/releases'
        params = {"token": self.token}
        response = self.get(url=base_url, params=params)
        data = response.json()

        total_pages = data['pagination']['pages']
        total_items = data['pagination']['items']
        print(f"Total pages: {total_pages}, Total items: {total_items}")

        releases = []
        for page in range(1, total_pages + 1):
            print(f"Getting page {page} / {total_pages}")
            params['page'] = page
            response = self.get(url=base_url, params=params)
            data = response.json()
            releases.extend(data['releases'])
        return releases
    
    def get_label_tracks(self, label_id):
        print(f"Getting label tracks for {label_id}")
        releases = self.get_label_releases(label_id)
        all_tracks = []
        for i, release in enumerate(releases):
            print(f"Getting release tracks for {release['id']} ({i+1}/{len(releases)})")
            tracks = self.get_release_tracks(release['id'])
            all_tracks.extend(tracks)
        print(f"Got {len(all_tracks)} tracks")
        return all_tracks


if __name__ == "__main__":
    d = Discogs()
    data = d.search(
       style="Psy-Trance,Progressive Trance",
       format="Compilation",
       year="2000-2009",
       sort="have",
       sort_order="desc",
       )
    print(data)

    #artist_id = 108713  # Example artist ID
    #d.get_artist_releases(artist_id)

    # tracks = d.get_release_tracks(108713)
    # for track in tracks:
    #     print(track)

    # artist_id = 170719
    # tracks = d.get_artist_tracks(artist_id)
    # for track in tracks:
    #     print(track)

    # label_id = 6951
    # tracks = d.get_label_tracks(label_id)
    # for track in tracks:
    #     print(track)
