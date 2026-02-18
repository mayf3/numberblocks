#!/usr/bin/env python3
"""
Simple Series Downloader
Downloads episodes from YouTube based on YAML configuration
"""
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


def sanitize_title(title: str) -> str:
    """Clean title for filename."""
    title = re.sub(r'[^\w\s-]', '', title)
    title = title.replace(' ', '_')
    title = re.sub(r'_+', '_', title)
    return title.strip('_')


def parse_episode_info(title: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse season and episode from S##E## format in title."""
    match = re.search(r'[Ss](\d+)[Ee](\d+)', title)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def generate_filename(config: dict, season: int, episode: int, title: str) -> str:
    """Generate filename based on config pattern."""
    pattern = config.get('naming_pattern', 'S{season:02d}E{episode:02d}_{title}.mp4')
    clean_title = re.sub(r'^[Ss]\d+[Ee]\d+\s*', '', title)
    clean_title = sanitize_title(clean_title)
    return pattern.format(
        season=season,
        episode=episode,
        title=clean_title
    )


def get_season_dir(download_dir: Path, series_name: str, season_num: int, config: dict) -> Path:
    """Generate season directory path."""
    pattern = config.get('directory_pattern', '{series_name}_Season_{season}')
    dir_name = pattern.format(
        series_name=series_name.replace(' ', '_'),
        season=season_num
    )
    return download_dir / dir_name


def check_existing_file(season_dir: Path, season: int, episode: int) -> bool:
    """Check if episode already exists."""
    if not season_dir.exists():
        return False
    
    for file_path in season_dir.glob("*.mp4"):
        match = re.search(r'[Ss](\d+)[Ee](\d+)', file_path.name)
        if match and int(match.group(1)) == season and int(match.group(2)) == episode:
            return True
    return False


def download_episode(video_id: str, season: int, episode: int, title: str,
                    output_path: Path, config: dict) -> bool:
    """Download single episode."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if check_existing_file(output_path.parent, season, episode):
        print(f"  [SKIP] S{season:02d}E{episode:02d} already exists")
        return True
    
    quality = config.get('quality', 1080)
    cmd = [
        "python3", "-m", "yt_dlp",
        "-f", f"best[height<={quality}]",
        "-o", str(output_path),
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    subtitles = config.get('subtitles', {})
    if subtitles.get('enabled', False):
        cmd.extend(["--write-sub", "--sub-lang", subtitles.get('lang', 'en')])
        if subtitles.get('embed', False):
            cmd.append("--embed-subs")
    
    print(f"  [DOWNLOAD] S{season:02d}E{episode:02d}: {title[:40]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"    ✓ Success")
        return True
    else:
        error = result.stderr[:100] if result.stderr else "Unknown error"
        print(f"    ✗ Failed: {error}")
        return False


def main():
    """Main entry."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download series from YouTube')
    parser.add_argument('config', help='Series config name (e.g., numberblocks, peppa_pig)')
    parser.add_argument('--config-dir', default='config/series',
                       help='Directory containing series config files')
    parser.add_argument('--download-dir', default='downloads',
                       help='Download directory')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config_dir) / f"{args.config}.yaml"
    if not config_path.exists():
        print(f"Error: Config not found: {config_path}", file=sys.stderr)
        print(f"\nAvailable configs:")
        for f in sorted(Path(args.config_dir).glob('*.yaml')):
            print(f"  - {f.stem}")
        return 1
    
    config = load_config(config_path)
    series_name = config['series_name']
    
    # Get episodes from config
    episodes = config.get('episodes', {})
    if not episodes:
        print(f"Error: No episodes defined in config", file=sys.stderr)
        return 1
    
    total = sum(len(eps) for eps in episodes.values())
    
    download_dir = Path(args.download_dir)
    
    print("=" * 60)
    print(f"Downloading: {series_name}")
    print("=" * 60)
    print(f"Total episodes: {total}")
    print(f"Download directory: {download_dir.absolute()}")
    print()
    
    # Confirmation
    if not args.yes:
        response = input("Start downloading? [Y/n]: ").strip().lower()
        if response and response not in ('y', 'yes'):
            print("Cancelled.")
            return 0
    
    # Download
    success = skipped = failed = 0
    
    for season_name, season_episodes in episodes.items():
        print(f"\n{'=' * 60}")
        print(f"{season_name} ({len(season_episodes)} episodes)")
        print(f"{'=' * 60}")
        
        for ep in season_episodes:
            season_num, episode_num = parse_episode_info(ep['title'])
            
            if not season_num or not episode_num:
                print(f"  [WARN] Cannot parse: {ep['title'][:40]}")
                failed += 1
                continue
            
            season_dir = get_season_dir(download_dir, series_name, season_num, config)
            filename = generate_filename(config, season_num, episode_num, ep['title'])
            output_path = season_dir / filename
            
            result = download_episode(
                ep['id'], season_num, episode_num, ep['title'],
                output_path, config
            )
            
            if result:
                if check_existing_file(season_dir, season_num, episode_num):
                    skipped += 1
                else:
                    success += 1
            else:
                failed += 1
    
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Downloaded: {success}")
    print(f"  Skipped:    {skipped}")
    print(f"  Failed:     {failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
