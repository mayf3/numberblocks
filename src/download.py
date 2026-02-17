#!/usr/bin/env python3
"""
Numberblocks Downloader - Simple & Working
Downloads episodes from YouTube playlists in 1080p HD
"""
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Tuple, Optional

# Configuration
PLAYLISTS_FILE = Path("playlists.json")
DOWNLOAD_DIR = Path("downloads")
ARCHIVE_FILE = Path("downloaded.txt")

def load_playlists() -> Dict:
    """Load episode data from playlists.json."""
    if not PLAYLISTS_FILE.exists():
        raise FileNotFoundError(f"{PLAYLISTS_FILE} not found. Run: python3 src/fetch_playlists.py")
    
    with open(PLAYLISTS_FILE, encoding='utf-8') as f:
        return json.load(f)

def sanitize_title(title: str) -> str:
    """Clean title for filename."""
    # Remove special characters but keep alphanumeric, spaces, hyphens
    title = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    # Remove multiple consecutive underscores
    title = re.sub(r'_+', '_', title)
    # Remove leading/trailing underscores
    return title.strip('_')

def parse_episode_info(title: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse season and episode from title."""
    # Pattern: "... S1 E1 | ..." or "... Full Episode - S1 E1 | ..."
    match = re.search(r'S(\d+)\s*E(\d+)', title)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def check_existing_file(season: int, episode: int) -> bool:
    """Check if episode already exists in any format."""
    season_dir = DOWNLOAD_DIR / f"Season_{season}_HD"
    if not season_dir.exists():
        return False
    
    # Get all mp4 files and check if any match the season/episode
    for file_path in season_dir.glob("*.mp4"):
        filename = file_path.name
        # Look for SXXEXX pattern in filename (case insensitive)
        match = re.search(r'[Ss](\d+)[Ee](\d+)', filename)
        if match:
            file_season = int(match.group(1))
            file_episode = int(match.group(2))
            if file_season == season and file_episode == episode:
                return True
    
    return False

def download_episode(video_id: str, season: int, episode: int, title: str) -> bool:
    """Download single episode."""
    season_dir = DOWNLOAD_DIR / f"Season_{season}_HD"
    season_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded (flexible matching)
    if check_existing_file(season, episode):
        print(f"  [SKIP] Already exists: S{season}E{episode}")
        return True
    
    clean_title = sanitize_title(title)
    output_template = str(season_dir / f"S{season:02d}E{episode:02d}_{clean_title}.mp4")
    
    cmd = [
        "python3", "-m", "yt_dlp",
        "-f", "best[height<=1080]",
        "--write-sub", "--sub-lang", "en",
        "--embed-subs",
        "--download-archive", str(ARCHIVE_FILE),
        "-o", output_template,
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    print(f"  [DOWNLOAD] S{season}E{episode}: {title[:50]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"    ✓ Success")
        return True
    else:
        error_msg = result.stderr[:150] if result.stderr else "Unknown error"
        print(f"    ✗ Failed: {error_msg}")
        return False

def main():
    """Main download loop."""
    print("=" * 60)
    print("Numberblocks Downloader")
    print("=" * 60)
    
    # Load data
    playlists = load_playlists()
    total_episodes = sum(s['episode_count'] for s in playlists.values())
    print(f"\nFound {len(playlists)} seasons, {total_episodes} episodes")
    print(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    print(f"Archive file: {ARCHIVE_FILE}")
    
    # Count existing episodes
    existing_count = 0
    for season_dir in DOWNLOAD_DIR.glob("Season_*_HD"):
        existing_count += len(list(season_dir.glob("*.mp4")))
    print(f"Already downloaded: {existing_count} episodes")
    print()
    
    # Ask for confirmation
    response = input("Start downloading missing episodes? [Y/n]: ").strip().lower()
    if response and response not in ('y', 'yes'):
        print("Cancelled.")
        return 0
    
    # Download all
    success = 0
    failed = 0
    skipped = 0
    
    for season_name, season_data in playlists.items():
        print(f"\n{'=' * 60}")
        print(f"Processing {season_name} ({season_data['episode_count']} episodes)")
        print(f"{'=' * 60}")
        
        for ep in season_data['episodes']:
            season_num, episode_num = parse_episode_info(ep['title'])
            
            if not season_num or not episode_num:
                print(f"  [WARN] Cannot parse: {ep['title'][:50]}")
                failed += 1
                continue
            
            result = download_episode(
                ep['id'], 
                season_num, 
                episode_num, 
                ep['title']
            )
            
            if result:
                if check_existing_file(season_num, episode_num):
                    skipped += 1
                else:
                    success += 1
            else:
                failed += 1
    
    # Summary
    print(f"\n{'=' * 60}")
    print("DOWNLOAD SUMMARY")
    print(f"{'=' * 60}")
    print(f"  New downloads: {success}")
    print(f"  Skipped:       {skipped}")
    print(f"  Failed:        {failed}")
    print(f"  Total:         {success + skipped + failed}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
