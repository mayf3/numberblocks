#!/usr/bin/env python3
"""
Generic Series Downloader
Downloads episodes from YouTube playlists in 1080p HD
Supports multiple series via YAML configuration files
"""
import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

import yaml


def load_config(config_path: Path) -> dict:
    """Load series configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_playlists(playlists_file: Path) -> Dict:
    """Load episode data from playlists JSON."""
    if not playlists_file.exists():
        raise FileNotFoundError(
            f"{playlists_file} not found. Run: python3 src/fetch_playlists.py <series>"
        )
    
    with open(playlists_file, encoding='utf-8') as f:
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


def get_season_dir(download_dir: Path, series_name: str, season_num: int, 
                   config: dict, season_name: str = "") -> Path:
    """Generate season directory path based on config pattern."""
    pattern = config.get('directory_pattern', 'Season_{season}_HD')
    dir_name = pattern.format(
        series_name=series_name,
        season=season_num,
        season_name=season_name
    )
    return download_dir / dir_name


def generate_filename(config: dict, season: int, episode: int, title: str) -> str:
    """Generate filename based on config pattern."""
    pattern = config.get('naming_pattern', 'S{season:02d}E{episode:02d}_{title}.mp4')
    clean_title = sanitize_title(title)
    return pattern.format(
        season=season,
        episode=episode,
        title=clean_title
    )


def check_existing_file(season_dir: Path, season: int, episode: int) -> bool:
    """Check if episode already exists in any format."""
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


def download_episode(video_id: str, season: int, episode: int, title: str,
                    season_dir: Path, config: dict, archive_file: Path) -> bool:
    """Download single episode."""
    season_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded (flexible matching)
    if check_existing_file(season_dir, season, episode):
        print(f"  [SKIP] Already exists: S{season}E{episode}")
        return True
    
    filename = generate_filename(config, season, episode, title)
    output_template = str(season_dir / filename)
    
    # Build yt-dlp command based on config
    quality = config.get('quality', 1080)
    cmd = [
        "python3", "-m", "yt_dlp",
        "-f", f"best[height<={quality}]",
        "-o", output_template,
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    # Add subtitle options if enabled
    subtitles = config.get('subtitles', {})
    if subtitles.get('enabled', True):
        cmd.extend(["--write-sub", "--sub-lang", subtitles.get('lang', 'en')])
        if subtitles.get('embed', True):
            cmd.append("--embed-subs")
    
    # Add archive file
    cmd.extend(["--download-archive", str(archive_file)])
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Download series from YouTube')
    parser.add_argument('config', nargs='?', default='numberblocks',
                       help='Series config name (default: numberblocks)')
    parser.add_argument('--config-dir', default='config/series',
                       help='Directory containing series config files')
    parser.add_argument('--download-dir', default='downloads',
                       help='Download directory')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config_dir) / f"{args.config}.yaml"
    try:
        config = load_config(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nAvailable configs:")
        config_dir = Path(args.config_dir)
        if config_dir.exists():
            for f in sorted(config_dir.glob('*.yaml')):
                print(f"  - {f.stem}")
        return 1
    
    series_name = config['series_name']
    safe_name = series_name.lower().replace(' ', '_')
    
    # Load playlists
    playlists_file = Path(f"{safe_name}_playlists.json")
    try:
        playlists = load_playlists(playlists_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    download_dir = Path(args.download_dir)
    archive_file = Path(f"{safe_name}_downloaded.txt")
    
    print("=" * 60)
    print(f"{series_name} Downloader")
    print("=" * 60)
    
    total_episodes = sum(s['episode_count'] for s in playlists.values())
    print(f"\nFound {len(playlists)} seasons, {total_episodes} episodes")
    print(f"Download directory: {download_dir.absolute()}")
    print(f"Archive file: {archive_file}")
    
    # Count existing episodes
    existing_count = 0
    for season_dir in download_dir.glob("*_HD"):
        existing_count += len(list(season_dir.glob("*.mp4")))
    print(f"Already downloaded: {existing_count} episodes")
    print()
    
    # Ask for confirmation (unless --yes)
    if not args.yes:
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
            
            # Get season directory based on config
            season_dir = get_season_dir(
                download_dir, series_name, season_num, config, season_name
            )
            
            result = download_episode(
                ep['id'], 
                season_num, 
                episode_num, 
                ep['title'],
                season_dir,
                config,
                archive_file
            )
            
            if result:
                if check_existing_file(season_dir, season_num, episode_num):
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
