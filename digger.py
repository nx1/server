from flask import Flask, render_template, request
from discogs import Discogs
import os

app = Flask(__name__)
discogs = Discogs()

@app.route('/', methods=['GET', 'POST'])
def index():
    tracks =[]
    artist_name = ''
    if request.method == 'POST':
        artist_name = request.form.get('artist', '')
        tracks = discogs.search_artist_tracks(artist_name)
    return render_template('digger.html', tracks=tracks, artist_name=artist_name)

if __name__ == '__main__':
    app.run(debug=True)
