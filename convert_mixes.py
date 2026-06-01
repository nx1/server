#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def convert_file(input_path, output_path, format_type, bitrate, ss=None, to=None):
    """
    Converts audio file using ffmpeg, optionally cropping it.
    """
    print(f"Converting:\n  Input:  {input_path}\n  Output: {output_path}")
    if ss or to:
        print(f"  Cropping: {ss if ss else 'start'} to {to if to else 'end'}")
    
    # Base ffmpeg command
    cmd = ['ffmpeg', '-y']
    
    # If we put -ss before -i, it seeks quickly. For WAV, it is extremely fast.
    if ss:
        cmd += ['-ss', ss]
        
    cmd += ['-i', str(input_path)]
    
    # If we seek before -i, -to refers to the input source timeline, but placing it after -i with -to can sometimes be tricky.
    # Actually, if -ss is before -i, we should use -t (duration) instead of -to to be safe, or just put -ss and -to after -i.
    # Let's put -ss and -to after -i to keep timeline values absolute and simple.
    cmd = ['ffmpeg', '-y', '-i', str(input_path)]
    if ss:
        cmd += ['-ss', ss]
    if to:
        cmd += ['-to', to]
    
    if format_type == 'mp3':
        # -codec:a libmp3lame -b:a 256k
        cmd += ['-codec:a', 'libmp3lame', '-b:a', bitrate]
    elif format_type == 'opus':
        # -codec:a libopus -b:a 128k -vbr on
        cmd += ['-codec:a', 'libopus', '-b:a', bitrate, '-vbr', 'on']
    else:
        print(f"Unsupported target format: {format_type}")
        return False
        
    cmd.append(str(output_path))
    
    try:
        # Run conversion showing progress
        subprocess.run(cmd, check=True)
        print("✓ Conversion successful!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ ffmpeg failed with exit code {e.returncode}\n")
        return False

def update_mixes_json(title_keywords, output_filename):
    """
    Attempts to update mixes.json by matching keywords from the title.
    """
    json_path = Path(__file__).parent / 'mixes' / 'mixes.json'
    if not json_path.exists():
        print("mixes.json not found, skipping auto-update.")
        return
        
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        updated = False
        # Try matching by title keywords (case-insensitive)
        keywords = [k.lower() for k in title_keywords.split() if len(k) > 2]
        
        for mix in data:
            title_lower = mix.get('title', '').lower()
            # If we match most keywords, or if title contains the search string
            if title_keywords.lower() in title_lower or (keywords and all(k in title_lower for k in keywords)):
                old_file = mix.get('file')
                mix['file'] = output_filename
                updated = True
                print(f"Updated mixes.json entry '{mix['title']}' to use file '{output_filename}' (was '{old_file}')")
                break
                
        if updated:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Could not find a matching mix in mixes.json for search query: '{title_keywords}'")
            print("Please update mixes.json manually by setting:")
            print(f'  "file": "{output_filename}"')
            
    except Exception as e:
        print(f"Error updating mixes.json: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert WAV/FLAC/AIFF mixes to MP3 or Opus for streaming.")
    parser.add_argument("input_file", help="Path to the source audio file (WAV, FLAC, AIFF, etc.)")
    parser.add_argument("--format", choices=['mp3', 'opus'], default='opus', help="Target format: mp3 or opus (default: opus)")
    parser.add_argument("--bitrate", help="Target bitrate (default: 128k for opus, 256k for mp3)")
    parser.add_argument("--ss", help="Start time for cropping (e.g. HH:MM:SS or seconds)")
    parser.add_argument("--to", help="End time for cropping (e.g. HH:MM:SS or seconds)")
    parser.add_argument("--output-name", help="Custom output filename (otherwise uses input filename with target extension)")
    parser.add_argument("--match-title", dest="match_title", help="Title keyword to match in mixes.json to automatically update its 'file' field")
    
    args = parser.parse_args()
    
    if not check_ffmpeg():
        print("Error: 'ffmpeg' is not installed or not in system PATH. Please install it first.")
        sys.exit(1)
        
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
        
    # Default bitrates
    bitrate = args.bitrate
    if not bitrate:
        bitrate = '192k' if args.format == 'opus' else '320k'
        
    # Target directory: static/mixes/
    target_dir = Path(__file__).parent / 'static' / 'mixes'
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Output file name and path
    ext = '.opus' if args.format == 'opus' else '.mp3'
    output_filename = args.output_name if args.output_name else input_path.with_suffix(ext).name
    output_path = target_dir / output_filename
    
    if convert_file(input_path, output_path, args.format, bitrate, ss=args.ss, to=args.to):
        if args.match_title:
            update_mixes_json(args.match_title, output_filename)
        else:
            print("To link this file in mixes.json, add or update the entry with:")
            print(f'  "file": "{output_filename}"')

if __name__ == "__main__":
    main()
