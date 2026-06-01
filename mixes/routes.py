import os
import json
from flask import Blueprint, render_template, current_app

app = Blueprint('mixes', __name__)

@app.route('/')
def index():
    # Load metadata from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'mixes.json')
    mix_data = []
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            mix_data = json.load(f)
    
    # Check for local files in static/mixes
    mixes_dir = os.path.join(current_app.static_folder, 'mixes')
    if not os.path.exists(mixes_dir):
        os.makedirs(mixes_dir)
        
    valid_extensions = ('.mp3', '.ogg', '.wav', '.m4a', '.opus')
    local_files = [f for f in os.listdir(mixes_dir) if f.lower().endswith(valid_extensions)]
    
    mime_types = {
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.opus': 'audio/ogg; codecs=opus',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4'
    }
    
    # Enrich JSON data with local file status
    for mix in mix_data:
        file_name = mix.get('file')
        if file_name and file_name in local_files:
            mix['local_exists'] = True
            _, ext = os.path.splitext(file_name.lower())
            mix['local_mime'] = mime_types.get(ext, 'audio/mpeg')
        else:
            mix['local_exists'] = False
            mix['local_mime'] = None
            
    return render_template('mixes.html', mixes=mix_data)
