from flask import Flask, render_template, request
from discogs import Discogs
import os

app = Flask(__name__)
discogs = Discogs()

@app.route('/', methods=['GET', 'POST'])
def index():
    tracks = []
    query = ''
    search_type = 'artist'
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        search_type = request.form.get('search_type', 'artist')
        
        if query:
            if search_type == 'artist':
                tracks = discogs.search_artist_tracks(query)
            else:
                tracks = discogs.search_label_tracks(query)
    
    return render_template('digger.html', 
                         tracks=tracks, 
                         query=query,
                         search_type=search_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
