#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

# Hardcoded mappings between SSD file names (in /mnt/mixes/) and mixes.json entries
MAPPINGS = {
    "psyrock the mix.flac": "The PsyRock Mix",
    "100follower.flac": "100 Follower Special!",
    "Influence Ears - Norman Khan.wav": "IYE003 - Norman Khan (Influence Ears)",
    "silky smooth psyprog.wav": "Another round of silky smooth psy-prog from the turn of the millennia :D",
    "Generator b2b Norman Khan.wav": "Norman Khan b2b Generator - The Shadow Dance: A Dark Journey",
    "25 Prog trance tunes in 1 hr.wav": "Is it possible to mix 25 ancient progressive trance tracks in under an hour?",
    "Maximalist Trance.wav": "Maximalist Trance",
    "Tribal Mix.wav": "Tribal Mix",
    "A Trip to Progington.wav": "A trip to progington",
    "sound of whomp.wav": "Sound of Whomp w/ Norman Khan",
    "2022_EOY_mix.wav": "2022 End of Year Mix",
    "Solar Summer Blowout 11_06 .wav": "Live @ Sobar Southampton (1:23 - 2:03)",
    "SEMSU Livestream 13_6_20.wav": "SEMSU Charity livestream (Video)",
    "Norman Khan b2b generator - Ancient Circuits.flac": "Norman Khan b2b Generator - Ancient Circuits"
}

SSD_DIR = Path("/mnt/mixes")
STATIC_DIR = Path(__file__).parent / "static" / "mixes"
JSON_PATH = Path(__file__).parent / "mixes" / "mixes.json"
CONVERT_SCRIPT = Path(__file__).parent / "convert_mixes.py"

# Special configuration for cropping and renaming mixes
SPECIAL_PROCESSING = {
    "Solar Summer Blowout 11_06 .wav": {
        "output_name": "semsu_summer_blowout_11_06_2022.opus",
        "ss": "01:23:00",
        "to": "02:03:00"
    }
}

def get_mixes_json():
    if not JSON_PATH.exists():
        return []
    with open(JSON_PATH, "r") as f:
        return json.load(f)

def save_mixes_json(data):
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def status():
    print("=== Mix Conversion Status ===")
    if not SSD_DIR.exists():
        print(f"Error: SSD directory '{SSD_DIR}' is not accessible.")
        return False
        
    mix_data = get_mixes_json()
    local_files = os.listdir(STATIC_DIR) if STATIC_DIR.exists() else []
    
    # Track files on SSD
    ssd_files = os.listdir(SSD_DIR)
    
    print("\nMapped Files:")
    print(f"{'SSD Filename':<40} | {'Status':<15} | {'Mix Title'}")
    print("-" * 85)
    
    for filename, title in MAPPINGS.items():
        exists_on_ssd = filename in ssd_files
        spec = SPECIAL_PROCESSING.get(filename, {})
        target_name = spec.get("output_name", Path(filename).with_suffix(".opus").name)
        exists_locally = target_name in local_files
        
        status_str = "Not on SSD"
        if exists_on_ssd:
            status_str = "Converted" if exists_locally else "Ready to Convert"
            
        print(f"{filename:<40} | {status_str:<15} | {title}")
        
    print("\nUnmapped Files on SSD:")
    for filename in ssd_files:
        if filename in MAPPINGS:
            continue
        # Skip duplicates or metadata files
        if filename in ["100follower.wav", "100follower.mp3", "psyrock1_2.wav"] or filename.startswith("."):
            continue
        spec = SPECIAL_PROCESSING.get(filename, {})
        target_name = spec.get("output_name", Path(filename).with_suffix(".opus").name)
        exists_locally = target_name in local_files
        status_str = "Converted" if exists_locally else "Ready to Convert"
        print(f"{filename:<40} | {status_str:<15} | (No matching entry in mixes.json)")
        
    print("\n=============================")
    return True

def run_conversion(filename, title=None, create_new=False):
    input_path = SSD_DIR / filename
    if not input_path.exists():
        print(f"Error: Source file '{input_path}' not found.")
        return False
        
    spec = SPECIAL_PROCESSING.get(filename, {})
    output_name = spec.get("output_name", input_path.with_suffix(".opus").name)
    output_path = STATIC_DIR / output_name
    
    if output_path.exists():
        print(f"→ '{output_name}' already exists in static/mixes. Skipping conversion.")
    else:
        # Run conversion script
        print(f"⚡ Converting '{filename}' to Opus...")
        cmd = [sys.executable, str(CONVERT_SCRIPT), str(input_path), "--format", "opus", "--output-name", output_name]
        if "ss" in spec:
            cmd += ["--ss", spec["ss"]]
        if "to" in spec:
            cmd += ["--to", spec["to"]]
            
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print(f"✗ Failed converting {filename}")
            return False
            
    # Update JSON
    mix_data = get_mixes_json()
    updated = False
    
    if title:
        for mix in mix_data:
            if mix.get("title", "").lower() == title.lower():
                mix["file"] = output_name
                updated = True
                print(f"✓ Updated mixes.json entry '{mix['title']}' file name to '{output_name}'")
                break
                
    if not updated and create_new:
        # Create a new entry for unmapped files
        # Let's extract a clean title from the filename
        clean_title = Path(filename).stem.replace("_", " ").title()
        if "B2b" in clean_title:
            clean_title = clean_title.replace("B2b", "b2b")
            
        new_entry = {
            "date": "31/05/2026",
            "title": clean_title,
            "file": output_name,
            "links": {},
            "tracklist": []
        }
        mix_data.insert(0, new_entry) # Add to top
        updated = True
        print(f"✓ Created new mixes.json entry '{clean_title}' with file '{output_name}'")
        
    if updated:
        save_mixes_json(mix_data)
        
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  batch_convert.py status           # Check which files exist and their statuses")
        print("  batch_convert.py all              # Convert all mapped files from SSD")
        print("  batch_convert.py unmatched        # Convert unmatched files and add them to mixes.json")
        print("  batch_convert.py <filename>       # Convert a single specific SSD file and map it")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "status":
        status()
    elif cmd == "all":
        ssd_files = os.listdir(SSD_DIR) if SSD_DIR.exists() else []
        success_count = 0
        for filename, title in MAPPINGS.items():
            if filename in ssd_files:
                if run_conversion(filename, title):
                    success_count += 1
        print(f"\nDone! Successfully processed {success_count} mixes.")
    elif cmd == "unmatched":
        ssd_files = os.listdir(SSD_DIR) if SSD_DIR.exists() else []
        success_count = 0
        for filename in ssd_files:
            if filename in MAPPINGS:
                continue
            if filename in ["100follower.wav", "100follower.mp3", "psyrock1_2.wav"] or filename.startswith("."):
                continue
            # It's an unmatched audio file
            if filename.lower().endswith((".flac", ".wav", ".aiff", ".aif", ".mp3", ".m4a")):
                if run_conversion(filename, create_new=True):
                    success_count += 1
        print(f"\nDone! Successfully processed {success_count} unmatched mixes.")
    else:
        # Single file
        filename = cmd
        title = MAPPINGS.get(filename)
        if not title:
            # If not in mappings, check if it's on SSD
            ssd_files = os.listdir(SSD_DIR) if SSD_DIR.exists() else []
            if filename in ssd_files:
                run_conversion(filename, create_new=True)
            else:
                print(f"Error: '{filename}' not found in mappings or on SSD.")
        else:
            run_conversion(filename, title)

if __name__ == "__main__":
    main()
