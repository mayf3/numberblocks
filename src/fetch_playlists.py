#!/usr/bin/env python3
"""
Fetch all season playlists from YouTube for configured series.
Supports multiple series via YAML configuration files.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict:
    """Load series configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def fetch_playlist_info(playlist_id: str, timeout: int = 60) -> list:
    """Fetch playlist metadata using yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            f"https://www.youtube.com/playlist?list={playlist_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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
        print(f"  Error fetching playlist {playlist_id}: {e}", file=sys.stderr)
        return []


def fetch_series(config: dict, output_dir: Path) -> None:
    """Fetch all playlists for a series and save to JSON."""
    series_name = config['series_name']
    print(f"\n{'='*60}")
    print(f"Fetching: {series_name}")
    print(f"{'='*60}")
    
    all_data = {}
    seasons = config.get('seasons', {})
    
    for season_name, playlist_id in seasons.items():
        print(f"\nFetching {season_name}...")
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
    safe_name = series_name.lower().replace(' ', '_')
    output_path = output_dir / f"{safe_name}_playlists.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {output_path}")
    print(f"  Total seasons: {len(all_data)}")
    print(f"  Total episodes: {sum(s['episode_count'] for s in all_data.values())}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch YouTube playlist metadata')
    parser.add_argument('config', nargs='?', default='numberblocks',
                       help='Series config name (default: numberblocks)')
    parser.add_argument('--config-dir', default='config/series',
                       help='Directory containing series config files')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for JSON files')
    
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
    
    # Fetch series data
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fetch_series(config, output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
