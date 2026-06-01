#!/usr/bin/env python3
import os
import json
from pathlib import Path
from PIL import Image

ARTWORK_DIR = Path(__file__).parent / "static" / "mixes" / "artwork"
JSON_PATH = Path(__file__).parent / "mixes" / "mixes.json"

# File extensions we want to optimize (keep icons like .ico or small UI pngs separate)
EXCLUDED_FILES = ["mixcloud.png", "soundcloud.png", "youtube.ico"]

def optimize_images():
    if not ARTWORK_DIR.exists():
        print(f"Error: Artwork directory '{ARTWORK_DIR}' does not exist.")
        return {}
        
    print("=== Optimizing Artwork Images ===")
    
    # Store old-to-new filename mappings
    filename_mappings = {}
    
    for item in ARTWORK_DIR.iterdir():
        if not item.is_file() or item.name in EXCLUDED_FILES or item.name.startswith("."):
            continue
            
        # Check if it's already a JPEG or PNG that needs compression
        if item.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            continue
            
        print(f"\nProcessing: {item.name} ({item.stat().st_size / (1024*1024):.2f} MB)")
        
        try:
            with Image.open(item) as img:
                # Convert to RGB (JPEGs do not support transparency/RGBA)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                # Determine target size
                if item.name == "sc_banner.png":
                    # Widescreen banner: Max width 1200px, keep aspect ratio
                    target_width = 1200
                    w_percent = (target_width / float(img.size[0]))
                    target_height = int((float(img.size[1]) * float(w_percent)))
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                else:
                    # Cover art: Resize to square 500x500px
                    img = img.resize((500, 500), Image.Resampling.LANCZOS)
                
                # New filename (change suffix to .jpg)
                new_filename = item.with_suffix(".jpg").name
                new_path = ARTWORK_DIR / new_filename
                
                # Save compressed JPEG (80% quality is visually transparent but tiny)
                img.save(new_path, "JPEG", quality=80, optimize=True)
                
                new_size = new_path.stat().st_size / 1024 # KB
                print(f"✓ Saved:      {new_filename} ({new_size:.1f} KB)")
                
                # Register mapping
                filename_mappings[item.name] = new_filename
                
                # If we changed file extension/compressed, delete the old file to save space
                if item.name != new_filename:
                    item.unlink()
                    print(f"✓ Deleted:    Original {item.name}")
                    
        except Exception as e:
            print(f"✗ Error optimizing {item.name}: {e}")
            
    return filename_mappings

def update_mixes_json(mappings):
    if not JSON_PATH.exists():
        print("mixes.json not found, skipping database update.")
        return
        
    try:
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            
        updated_count = 0
        for mix in data:
            artwork = mix.get("artwork")
            if artwork in mappings:
                mix["artwork"] = mappings[artwork]
                updated_count += 1
                
        if updated_count > 0:
            with open(JSON_PATH, "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n✓ Updated {updated_count} artwork entries in mixes.json!")
        else:
            print("\nNo entries in mixes.json needed updating.")
            
    except Exception as e:
        print(f"Error updating mixes.json: {e}")

def main():
    mappings = optimize_images()
    if mappings:
        update_mixes_json(mappings)
        print("\n=== Artwork Optimization Complete! ===")
    else:
        print("\nNo files required optimization.")

if __name__ == "__main__":
    main()
