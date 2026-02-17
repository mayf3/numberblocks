#!/usr/bin/env python3
"""
Numberblocks Complete Downloader
Downloads all episodes from direct_urls.json with proper naming and organization
"""
import json
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
import sys

class NumberblocksDownloader:
    """Downloads all Numberblocks episodes."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.direct_urls_file = self.base_dir / "direct_urls.json"
        self.download_archive = self.base_dir / "downloaded.txt"
        self.download_log = self.base_dir / "download.log"

        self.results = {
            'success': [],
            'failed': [],
            'skipped': []
        }

    def load_direct_urls(self) -> List[Dict]:
        """Load direct URLs from JSON file."""
        if not self.direct_urls_file.exists():
            raise FileNotFoundError(f"File {self.direct_urls_file} not found")

        with open(self.direct_urls_file, encoding='utf-8') as f:
            data = json.load(f)

        print(f"Loaded {len(data)} episodes from {self.direct_urls_file}")
        return data

    def sanitize_title(self, title: str) -> str:
        """Clean title for filename."""
        # Remove special characters but keep alphanumeric, spaces, hyphens
        title = re.sub(r'[^\w\s-]', '', title)
        # Replace spaces with underscores
        title = title.replace(' ', '_')
        # Remove multiple consecutive underscores
        title = re.sub(r'_+', '_', title)
        # Remove leading/trailing underscores
        title = title.strip('_')
        return title

    def parse_season_episode(self, item: Dict) -> tuple:
        """Parse season and episode numbers."""
        season = item['season']
        episode = item['episode']

        # Extract season number
        season_match = re.search(r'\d+', season)
        if not season_match:
            raise ValueError(f"Invalid season format: {season}")
        season_num = int(season_match.group())

        # Extract episode number
        episode_match = re.search(r'\d+', episode)
        if not episode_match:
            raise ValueError(f"Invalid episode format: {episode}")
        episode_num = int(episode_match.group())

        return season_num, episode_num

    def get_season_dir(self, season_num: int) -> Path:
        """Get or create season directory."""
        season_dir = self.base_dir / f"Season {season_num}"
        season_dir.mkdir(exist_ok=True)
        return season_dir

    def generate_filename(self, item: Dict, season_num: int, episode_num: int) -> str:
        """Generate filename for episode."""
        clean_title = self.sanitize_title(item['title'])
        return f"S{season_num:02d}E{episode_num:02d}-{clean_title}.mp4"

    def check_file_exists(self, season_dir: Path, filename: str) -> bool:
        """Check if file already exists and is valid."""
        filepath = season_dir / filename
        MIN_SIZE_BYTES = 10000
        if filepath.exists() and filepath.stat().st_size > MIN_SIZE_BYTES:
            return True
        return False

    def download_episode(self, item: Dict, idx: int, total: int) -> Dict:
        """Download a single episode."""
        try:
            season_num, episode_num = self.parse_season_episode(item)
            season_dir = self.get_season_dir(season_num)
            filename = self.generate_filename(item, season_num, episode_num)
            filepath = season_dir / filename

            # Check if already downloaded
            if self.check_file_exists(season_dir, filename):
                print(f"[OK] [{idx}/{total}] Already exists: {filename}")
                return {
                    'item': item,
                    'status': 'skipped',
                    'filepath': str(filepath)
                }

            # Download using yt-dlp
            video_id = item['video_id']
            direct_url = f"https://www.youtube.com/embed/{video_id}"

            print(f"[DOWNLOAD] [{idx}/{total}] Downloading: {filename}")
            print(f"   Season {season_num}, Episode {episode_num}")
            print(f"   Video ID: {video_id}")

            cmd = [
                "python3", "-m", "yt_dlp",
                "--extractor-args", "youtube:player_client=android,web",
                "-f", "best[height<=720]+bestaudio/best[height<=720]",
                "--write-sub", "--sub-lang", "en",
                "--write-auto-sub", "--sub-format", "vtt",
                "--embed-subs",
                "--ignore-errors",
                "--no-overwrites",
                "--continue",
                "--download-archive", str(self.download_archive),
                "-o", str(filepath),
                f"https://www.youtube.com/watch?v={video_id}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0 and filepath.exists():
                print(f"[OK] [{idx}/{total}] Success: {filename}")
                return {
                    'item': item,
                    'status': 'success',
                    'filepath': str(filepath)
                }
            else:
                error_msg = result.stderr or "Unknown error"
                print(f"[ERROR] [{idx}/{total}] Failed: {filename}")
                print(f"   Error: {error_msg[:200]}")
                return {
                    'item': item,
                    'status': 'failed',
                    'error': error_msg
                }

        except Exception as e:
            print(f"[ERROR] [{idx}/{total}] Exception: {str(e)}")
            return {
                'item': item,
                'status': 'failed',
                'error': str(e)
            }

    def download_all(self) -> Dict:
        """Download all episodes."""
        episodes = self.load_direct_urls()
        total = len(episodes)

        print(f"\n{'='*60}")
        print(f"Starting download of {total} episodes")
        print(f"{'='*60}\n")

        # Sequential download (safer than parallel)
        results = []
        for idx, item in enumerate(episodes, 1):
            result = self.download_episode(item, idx, total)
            results.append(result)

            # Categorize results
            if result['status'] == 'success':
                self.results['success'].append(result)
            elif result['status'] == 'skipped':
                self.results['skipped'].append(result)
            else:
                self.results['failed'].append(result)

        return self.results

    def print_summary(self):
        """Print download summary."""
        print(f"\n{'='*60}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*60}")
        print(f"[OK] Success: {len(self.results['success'])}")
        print(f"[SKIP]  Skipped: {len(self.results['skipped'])}")
        print(f"[ERROR] Failed: {len(self.results['failed'])}")
        print(f"[STATS] Total: {len(self.results['success']) + len(self.results['skipped']) + len(self.results['failed'])}")

        if self.results['failed']:
            print(f"\n[ERROR] Failed episodes:")
            for result in self.results['failed']:
                item = result['item']
                print(f"   - {item['season']} {item['episode']}: {item['title'][:50]}")

        print(f"{'='*60}\n")

    def save_report(self):
        """Save download report to JSON."""
        report_file = self.base_dir / "download_report.json"

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'success': len(self.results['success']),
                'skipped': len(self.results['skipped']),
                'failed': len(self.results['failed']),
                'total': len(self.results['success']) + len(self.results['skipped']) + len(self.results['failed'])
            },
            'results': self.results
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[FILE] Report saved to: {report_file}")

def main():
    """Main entry point."""
    print("="*60)
    print("Numberblocks Complete Downloader")
    print("="*60)

    try:
        downloader = NumberblocksDownloader()
        downloader.download_all()
        downloader.print_summary()
        downloader.save_report()

        # Exit with error code if any failures
        if downloader.results['failed']:
            return 1

        return 0

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
