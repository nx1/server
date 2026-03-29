from flask import Blueprint, render_template, request, Response, stream_with_context
from discogs import Discogs
import json

app = Blueprint('routes', __name__)
discogs = Discogs()

@app.route('/')
def index():
    return render_template('digger.html')

@app.route('/search')
def search():
    query       = request.args.get('query', '')
    search_type = request.args.get('search_type', 'artist')

    def generate():
        if not query:
            return

        try:
            if search_type == 'artist':
                # Check size before streaming
                search_results = discogs.search(query=query, type='artist', per_page=1)
                if not search_results['results']:
                    yield 'data: {"error": "Artist not found"}\n\n'
                    return

                artist = search_results['results'][0]
                artist_id = artist['id']

                # Warn if large
                releases_check = discogs.get(
                    f"https://api.discogs.com/artists/{artist_id}/releases",
                    page=1, per_page=1
                ).json()
                total = releases_check['pagination']['items']

                if total > discogs.ARTIST_MAX_RELEASES:
                    yield f'data: {json.dumps({"warning": f"Artist has {total} releases, showing first {discogs.ARTIST_MAX_RELEASES}"})}\n\n'

                for track in discogs.stream_artist_tracks(query):
                    yield f'data: {json.dumps(track)}\n\n'
            else:
                for track in discogs.stream_label_tracks(query):
                    yield f'data: {json.dumps(track)}\n\n'

        except Exception as e:
            print(f"Stream error: {e}")
            yield f'data: {json.dumps({"error": str(e)})}\n\n'

        yield 'data: {"done": true}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':     'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':        'keep-alive'
        }
    )
