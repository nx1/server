import os
from threading import Thread
import time
import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class Discogs:
    def __init__(self, **kwargs):
        self.token = os.getenv("DISCOGS_TOKEN")
        self.headers = {"User-Agent": "DiscogsAPI/1.0"}
        self.MAX_WORKERS = 3
        self.ARTIST_MAX_RELEASES = 100
    
    def get(self, url, **kwargs):
        params = {"token": self.token, **kwargs}
        
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 429:
                print(f"Rate limited, sleeping 60 seconds...")
                time.sleep(60)
                continue  # retry the same request
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} {response.text}")
                response.raise_for_status()
            
            if response.headers.get('x-discogs-ratelimit-remaining') == '1':
                print(f"Rate limit nearly exceeded, sleeping 10 seconds")
                time.sleep(10)
            
            return response

    def search(self, per_page=100, **kwargs):
        base_url = 'https://api.discogs.com/database/search'
        pagination = {'page': 1, 'per_page': per_page}
        params     = {**pagination, **kwargs}
        response   = self.get(base_url, **params)
        return response.json()

    def get_artist_releases(self, artist_id, sort='year', sort_order='desc'):
        base_url = f'https://api.discogs.com/artists/{artist_id}/releases'
        params = {"sort": sort, "sort_order": sort_order, "per_page": 100}
    
        first = self.get(base_url, **params, page=1).json()
        total_pages = first['pagination']['pages']
        total_items = first['pagination']['items']
        all_releases = list(first['releases'])
    
        if total_items > self.ARTIST_MAX_RELEASES:
            print(f"Artist has {total_items} releases, capping at {self.ARTIST_MAX_RELEASES}")
            return all_releases[:self.ARTIST_MAX_RELEASES]  # just return what we have from page 1
    
        def fetch_page(page):
            return self.get(base_url, **params, page=page).json()['releases']
    
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_page, p) for p in range(2, total_pages + 1)]
            for future in as_completed(futures):
                try:
                    all_releases.extend(future.result())
                except Exception as e:
                    print(f"Page fetch failed: {e}")
    
        return all_releases

    def get_label_releases(self, label_id, sort='year', sort_order='desc'):
        print(f"Getting label releases for {label_id}")
        base_url = f'https://api.discogs.com/labels/{label_id}/releases'
        params = {"token": self.token, "sort":sort, "sort_order":sort_order, "per_page":100}

        first = self.get(base_url, **params, page=1).json()
        total_pages = first['pagination']['pages']
        all_releases = list(first['releases'])

        def fetch_page(page):
            return self.get(base_url, **params, page=page).json()['releases']

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_page, p): p for p in range(2, total_pages + 1)}
            for future in as_completed(futures):
                all_releases.extend(future.result())

        return all_releases

    def get_artist_tracks(self, artist_id):
        print(f"Getting artist tracks for {artist_id}")
        releases = self.get_artist_releases(artist_id)
        all_tracks = []

        def process_release(release):
            if release['type'] == 'master':
                master  = self.get(release['resource_url']).json()
                release = self.get(master['main_release_url']).json()

            tracks = self.get_release_tracks(release_id=release['id'])

            result = []
            for track in tracks:
                if track['type_'] != 'track':
                    continue
                track['release'] = release # Add the release to the track
                if 'artists' in track:
                    # If the track has multiple artists, only include if our artist is one of them
                    if any(artist['id'] == artist_id for artist in track['artists']):
                        result.append(track)
                else: # Single artist release (album/EP)
                    result.append(track)
            return result

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [executor.submit(process_release, release) for release in releases]

            for future in as_completed(futures):
                try:
                    all_tracks.extend(future.result())
                except Exception as e:
                    print(f'A release failed to fetch: {e}')
            
        print(f"Got {len(all_tracks)} tracks")
        return all_tracks


    def stream_artist_tracks(self, artist_name):
        search_results = self.search(query=artist_name, type='artist', per_page=1)
        if not search_results['results']:
            return
        artist_id = search_results['results'][0]['id']
        releases = self.get_artist_releases(artist_id)
    
        for release in releases:
            if release['type'] == 'master':
                master  = self.get(release['resource_url']).json()       # fetch the master
                release = self.get(master['main_release_url']).json()    # then get main release from master
            
            tracks = self.get_release_tracks(release_id=release['id'])
            for track in tracks:
                if track['type_'] != 'track':
                    continue
                track['release'] = release
                if 'artists' in track:
                    if any(a['id'] == artist_id for a in track['artists']):
                        yield track
                else:
                    yield track

    def stream_label_tracks(self, label_name):
        """Generator version of search_label_tracks, yields tracks as they arrive."""
        search_result = self.search(query=label_name, type='label', per_page=1)
        if not search_result['results']:
            return
        label_id = search_result['results'][0]['id']

        releases = self.get_label_releases(label_id)

        for i, release in enumerate(releases):
            tracks = self.get_release_tracks(release_id=release['id'])
            for track in tracks:
                track['release'] = release
                yield track               # <-- yield instead of append


    
    def get_label_tracks(self, label_id):
        print(f"Getting label tracks for {label_id}")
        releases = self.get_label_releases(label_id)
        all_tracks = []

        def process_release(release):
            result = []
            tracks = self.get_release_tracks(release_id=release['id'])
            for track in tracks:
                track['release'] = release
            return tracks 

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [executor.submit(process_release, release) for release in releases]

            for future in as_completed(futures):
                try:
                    all_tracks.extend(future.result())
                except Exception as e:
                    print(f'A release failed to fetch: {e}')

        print(f"Got {len(all_tracks)} tracks")
        return all_tracks


       
    def get_release(self, release_id):
        base_url = f'https://api.discogs.com/releases/{release_id}'
        response = self.get(base_url)
        return response.json()

    def get_release_tracks(self, release_id):
        release = self.get_release(release_id)
        return release.get('tracklist', [])
    
    def get_master_tracks(self, master_id):
        pass


    def search_artist_tracks(self, artist_name):
        search_results = self.search(query=artist_name, type='artist', per_page=1)
        if len(search_results['results']) == 0:
            return [] 
        artist_id = search_results['results'][0]['id']
        tracks = self.get_artist_tracks(artist_id)
        return tracks 
    
    def search_label_tracks(self, label_name):
        search_result = self.search(query=label_name, type='label', per_page=1)
        if len(search_result['results']) == 0:
            return []
        label_id = search_result['results'][0]['id']
        tracks = self.get_label_tracks(label_id)
        return tracks


if __name__ == "__main__":
    d = Discogs()
    #release = d.get_release(108713)
    #videos = release['videos']
    #for video in videos:
    #    print(video)

    data = d.search(
       style="Psy-Trance,Progressive Trance",
       format="Compilation",
       year="2000-2009",
       sort="have",
       sort_order="desc",
       )
    print(data)

    # artist_id = 108713  
    # d.get_artist_releases(artist_id)
    # print(d)



    # tracks = d.get_release_tracks(108713)
    # print(tracks)
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
