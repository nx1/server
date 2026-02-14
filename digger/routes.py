from flask import Blueprint, render_template, request
from discogs import Discogs

# Create a blueprint for the routes
app = Blueprint('routes', __name__)
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
    
    return render_template('digger.html', tracks=tracks, query=query, search_type=search_type) 