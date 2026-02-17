#!/usr/bin/env python3
"""
Fetch all Numberblocks season playlists from YouTube.
Outputs playlists.json with metadata.
"""

import json
import subprocess
import sys
from pathlib import Path

# Known Numberblocks season playlists (verified manually)
PLAYLISTS = {
    "Season 1": "PL9swKX1PviEr9UfByZqJYiN8KX3AXqyXm",
    "Season 2": "PL9swKX1PviEru-LYxqyxH7rZGvw3zHQB",
    "Season 3": "PL9swKX1PviEruaholwotM1lOcNCQuweCl",
    "Season 4": "PL9swKX1PviEpcB-U4ugBkqPIGMYvQ5nP8",
    "Season 5": "PL9swKX1PviEph7heoMnLEfW2y28kwLNZw",
    "Season 6": "PL9swKX1PviEpqohvcXAr6KxPvuAzuFXVT",
    "Season 7": "PL9swKX1PviEovgpCesV8muL-i8RwogKvL",
    "Season 8": "PL9swKX1PviEo4WKwvN7y2vNiQkMfqNFUb",
}

def fetch_playlist_info(playlist_id):
    """Fetch playlist metadata using yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            f"https://www.youtube.com/playlist?list={playlist_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        lines = result.stdout.strip().split('\n')
        if not lines or lines == ['']:
            print(f"  Warning: Empty response for playlist {playlist_id}")
            return []
        videos = [json.loads(line) for line in lines if line.strip()]
        return videos
    except subprocess.TimeoutExpired:
        print(f"  Error: Timeout fetching playlist {playlist_id}", file=sys.stderr)
        return []
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching playlist {playlist_id}: {e}", file=sys.stderr)
        return []

def main():
    """Fetch all playlists and save metadata."""
    all_data = {}

    for season_name, playlist_id in PLAYLISTS.items():
        print(f"Fetching {season_name}...")
        videos = fetch_playlist_info(playlist_id)
        all_data[season_name] = {
            "playlist_id": playlist_id,
            "url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "episode_count": len(videos),
            "episodes": [
                {
                    "title": v.get("title"),
                    "id": v.get("id"),
                    "url": v.get("webpage_url"),
                    "duration": v.get("duration"),
                }
                for v in videos
            ]
        }
        print(f"  Found {len(videos)} episodes")

    # Save to JSON
    output_path = Path("playlists.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved playlist data to {output_path}")
    print(f"Total seasons: {len(all_data)}")
    print(f"Total episodes: {sum(s['episode_count'] for s in all_data.values())}")

if __name__ == "__main__":
    sys.exit(main())
