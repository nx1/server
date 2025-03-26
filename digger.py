from discogs import Discogs

discogs = Discogs()
artist = 'Insane Creation'
discogs.query(artist=artist)
print(discogs.json)
