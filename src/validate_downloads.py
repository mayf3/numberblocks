#!/usr/bin/env python3
"""
Validation script for downloaded Numberblocks videos
Checks file naming, organization, and completeness
"""
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def load_direct_urls(base_dir: Path) -> List[Dict]:
    """Load direct_urls.json."""
    urls_file = base_dir / "direct_urls.json"
    if not urls_file.exists():
        raise FileNotFoundError(f"❌ {urls_file} not found")

    with open(urls_file) as f:
        return json.load(f)

def parse_filename(filename: str) -> Dict | None:
    """Parse filename to extract season, episode, title."""
    # Expected format: S##E##-Title.mp4
    match = re.match(r'S(\d+)E(\d+)-(.+)\.mp4$', filename)
    if match:
        return {
            'season': int(match.group(1)),
            'episode': int(match.group(2)),
            'title': match.group(3)
        }
    return None

def scan_season_directory(season_dir: Path) -> List[Path]:
    """Scan season directory for MP4 files."""
    if not season_dir.exists():
        return []

    return list(season_dir.glob('*.mp4'))

def validate_videos(base_dir: Path) -> Dict:
    """Validate all downloaded videos."""
    results = {
        'total_expected': 0,
        'total_found': 0,
        'by_season': defaultdict(dict),
        'invalid_filenames': [],
        'missing_episodes': []
    }

    # Load expected episodes
    expected_episodes = load_direct_urls(base_dir)
    results['total_expected'] = len(expected_episodes)

    # Group by season
    expected_by_season = defaultdict(list)
    for ep in expected_episodes:
        season_match = re.search(r'\d+', ep['season'])
        if season_match:
            season_num = int(season_match.group())
            expected_by_season[season_num].append(ep)

    # Scan each season directory
    for season_num, expected_eps in expected_by_season.items():
        season_dir = base_dir / f"Season {season_num}"

        if not season_dir.exists():
            for ep in expected_eps:
                results['missing_episodes'].append(ep)
            continue

        # Scan for videos
        videos = scan_season_directory(season_dir)
        results['total_found'] += len(videos)
        results['by_season'][season_num]['expected'] = len(expected_eps)
        results['by_season'][season_num]['found'] = len(videos)
        results['by_season'][season_num]['videos'] = []

        for video_path in videos:
            parsed = parse_filename(video_path.name)

            if not parsed:
                results['invalid_filenames'].append(str(video_path))
                continue

            results['by_season'][season_num]['videos'].append({
                'path': str(video_path),
                'filename': video_path.name,
                'season': parsed['season'],
                'episode': parsed['episode'],
                'title': parsed['title'],
                'size_mb': video_path.stat().st_size / (1024*1024)
            })

    return results

def print_report(results: Dict):
    """Print validation report."""
    print("\n" + "="*60)
    print("NUMBERBLOCKS DOWNLOAD VALIDATION REPORT")
    print("="*60)

    print(f"\n📊 Overall:")
    print(f"   Expected: {results['total_expected']} episodes")
    print(f"   Found:    {results['total_found']} episodes")
    missing = results['total_expected'] - results['total_found']
    print(f"   Missing:  {missing} episodes")
    rate = results['total_found']/results['total_expected']*100 if results['total_expected'] > 0 else 0
    print(f"   Rate:     {rate:.1f}%")

    # By season
    print(f"\n📁 By Season:")
    for season in sorted(results['by_season'].keys()):
        data = results['by_season'][season]
        expected = data.get('expected', 0)
        found = data.get('found', 0)
        rate = found/expected*100 if expected > 0 else 0

        print(f"   Season {season}: {found}/{expected} ({rate:.0f}%)")

    # Invalid filenames
    if results['invalid_filenames']:
        print(f"\n❌ Invalid Filenames ({len(results['invalid_filenames'])}):")
        for filename in results['invalid_filenames']:
            print(f"   - {filename}")

    # Sample videos from each season
    print(f"\n📹 Sample Videos:")
    for season in sorted(results['by_season'].keys()):
        data = results['by_season'][season]
        videos = data.get('videos', [])

        if not videos:
            continue

        print(f"\n   Season {season}:")
        for video in videos[:3]:  # Show first 3
            print(f"     - S{video['season']:02d}E{video['episode']:02d}: {video['title'][:40]}")
            print(f"       Size: {video['size_mb']:.1f} MB")

        if len(videos) > 3:
            print(f"     ... and {len(videos) - 3} more")

    print("\n" + "="*60)

def save_report(base_dir: Path, results: Dict):
    """Save validation report to JSON."""
    report_file = base_dir / "validation_report.json"

    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Report saved to: {report_file}")

def main():
    """Main entry point."""
    base_dir = Path.cwd()

    if not (base_dir / "direct_urls.json").exists():
        print("❌ direct_urls.json not found")
        return 1

    results = validate_videos(base_dir)
    print_report(results)
    save_report(base_dir, results)

    return 0

if __name__ == "__main__":
    exit(main())
