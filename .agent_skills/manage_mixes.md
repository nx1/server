# Agent Skill: Managing the Mixes Page

This skill file contains context, architecture details, and Standard Operating Procedures (SOPs) for maintaining the custom DJ Mixes player on the home server. When requested to update, debug, or add new mixes, an agent should read this file using the `view_file` tool with `IsSkillFile=true` to gain context.

## 1. Architecture Overview
- **Data Source:** `/home/x1/server/mixes/mixes.json` (Parsed dynamically on every request; no server restart required for updates).
- **Backend Routing:** `/home/x1/server/mixes/routes.py` (Flask Blueprint checking for local files in `static/mixes`, including a POST endpoint to record play counts).
- **Frontend Template:** `/home/x1/server/templates/mixes.html` (Custom audio player UI with CSS grid and JS event listeners for playback, seeking, and logging play counts).
- **Audio Files:** Stored in `/home/x1/server/static/mixes/`.
- **Artwork:** Stored in `/home/x1/server/static/mixes/artwork/` (Must be optimized `.jpg` files, 500x500px).
- **Play Tracking:** Play counts are stored in `/home/x1/server/mixes/plays.json`. This file is ignored by git to keep development/deployment states clean. Play count increments are triggered via a POST request from the frontend JavaScript when a user begins playback (capped to once per page session per track).

## 2. Standard Operating Procedures (SOPs)

### Adding a New Mix
1. **Compress the Audio:** We do not host massive `.wav` files. All audio must be transcoded to 192 kbps Opus to respect residential bandwidth limits.
   ```bash
   ffmpeg -y -i "static/mixes/raw_mix.wav" -c:a libopus -b:a 192k "static/mixes/optimized_mix.opus"
   ```
2. **Update the Database:** Add or update the entry in `mixes.json`.
3. **Format the Tracklist:** The `tracklist` key must be a list of dictionaries with timestamps. Do not use plain text strings.
   ```json
   "tracklist": [
     { "time": "0:00:00", "artist": "Artist Name", "title": "Track Title" }
   ]
   ```
4. **Timestamp Formatting:** Always format timestamps using `H:MM:SS` (e.g. `0:00:00`, `0:03:28`, `1:15:45`). Do not use the short `MM:SS` format (e.g. `03:28` or `75:45`) to ensure consistency across all mix tracklists.

### Artwork Optimization
Artwork should be compressed JPEGs (not PNGs), but **do not crop them**. They must retain their original aspect ratios. If a new PNG or JPG is provided, optimize it using FFmpeg:
   ```bash
   ffmpeg -y -i "static/mixes/artwork/raw_poster.png" -q:v 5 "static/mixes/artwork/optimized_poster.jpg"
   ```
Then update the `artwork` key in `mixes.json` to link to the new `.jpg` file.

## 3. Known Pitfalls & Historical Bugs (Do Not Repeat)

- **Browser Connection Exhaustion (The "Hanging" Bug):**
  Never use `preload="metadata"` or `preload="auto"` on the `<audio>` tags in `mixes.html`. Modern browsers limit concurrent connections to 6 per domain. With 15+ mixes on the page, eager preloading saturates the browser's connection pool and causes new tabs to freeze indefinitely. **Always use `preload="none"`.**

- **Worker Thread Exhaustion (The "Server Crash" Bug):**
  The server runs Gunicorn with 9 workers and 4 threads. Never use synchronous blocking calls (like `time.sleep()`) in Python route handlers or instantiation logic (e.g., `sysinfo.py`). Doing so blocks the WSGI threads, causing the server to queue requests and eventually fail under load.

## 4. Deployment Context
- **OS:** Linux (Raspberry Pi/ARM Cortex-A76, 16GB RAM)
- **Service Name:** `pi-server.service`
- **Web Server:** Gunicorn (9 workers, gthread class) sitting behind Nginx.
- **Auto-Reload:** Flask is configured with `TEMPLATES_AUTO_RELOAD = True`. Changes to HTML templates or JSON data files take effect immediately upon page refresh.
