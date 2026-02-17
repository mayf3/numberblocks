#!/usr/bin/env python3
"""
Standardize Numberblocks video filenames to S##E##_Title.mp4 format.
Analyzes title metadata to determine correct season/episode numbers.
"""
import re
import shutil
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


def extract_info_from_filename(filename: str) -> Tuple[Optional[int], Optional[int], str]:
    """
    Extract season, episode, and title from filename.
    Handles various formats:
    - S01E01_Title.mp4 (correct)
    - S8E01_Title.mp4 (needs padding)
    - SP01_Title.mp4 (specials)
    - Title_S3E14.mp4 (wrong order)
    - S01E12-Title.mp4 (wrong separator)
    
    Returns: (season, episode, title_suffix)
    """
    # Try to find S#E# or SP# pattern
    # Standard format: S01E01_xxx
    standard_match = re.search(r'^[Ss](\d+)[Ee](\d+)', filename)
    
    if standard_match:
        season = int(standard_match.group(1))
        episode = int(standard_match.group(2))
        return season, episode, ""
    
    # Wrong order format: Title_S3E14.mp4
    wrong_order_match = re.search(r'[Ss](\d+)[Ee](\d+)(?!.*[Ss]\d+[Ee]\d+)', filename)
    if wrong_order_match:
        season = int(wrong_order_match.group(1))
        episode = int(wrong_order_match.group(2))
        return season, episode, ""
    
    # Specials format: SP01, Sp01, etc.
    sp_match = re.search(r'[Ss][Pp](\d+)', filename)
    if sp_match:
        episode = int(sp_match.group(1))
        return 0, episode, ""
    
    return None, None, ""


def clean_title(title: str) -> str:
    """Clean and standardize title portion of filename."""
    # First, remove everything from known separator patterns onwards
    # These are the YouTube-style suffixes
    title = re.split(r'\s*[｜|]\s*Full Episode', title)[0]
    title = re.split(r'\s*-\s*Full Episode', title)[0]
    title = re.split(r'\s*[｜|]\s*S\d+\s*E\d+', title)[0]
    title = re.split(r'\s*[｜|]\s*Learn to Count', title)[0]
    title = re.split(r'\s*[｜|]\s*Learn Times Tables', title)[0]
    title = re.split(r'\s*[｜|]\s*@Numberblocks', title)[0]
    title = re.split(r'\s*[｜|]\s*Numberblocks', title)[0]
    title = re.split(r'\s*-\s*Numbers Cartoon', title)[0]
    title = re.split(r'\s*\([^)]*\)\s*$', title)[0]
    
    # Replace special unicode characters with underscores or remove
    title = title.replace('｜', '_')
    title = title.replace('🔴', '')
    title = title.replace('🎅', '')
    title = title.replace('🎄', '')
    title = title.replace('🦸', '')
    title = title.replace('🔭', '')
    title = title.replace('🔮', '')
    title = title.replace('🪞', '')
    title = title.replace('🦖', '')
    title = title.replace('🚂', '')
    title = title.replace('🍇', '')
    title = title.replace('📖', '')
    title = title.replace('🎤', '')
    title = title.replace('👷', '')
    title = title.replace('👽', '')
    title = title.replace('🙈', '')
    title = title.replace('🌈', '')
    title = title.replace('🏁', '')
    title = title.replace('🎸', '')
    title = title.replace('🚀', '')
    title = title.replace('🟪', '')
    title = title.replace('⬢', '')
    title = title.replace('❄️', '')
    title = title.replace('🪞', '')
    title = title.replace('⚽️', '')
    title = title.replace('✨', '')
    title = title.replace('🧘', '')
    title = title.replace('♂️', '')
    title = title.replace('🌟', '')
    title = title.replace('🎶', '')
    title = title.replace('🛹', '')
    title = title.replace('📖', '')
    title = title.replace('🪜', '')
    title = title.replace('👑', '')
    title = title.replace('🟩', '')
    title = title.replace('🌝', '')
    title = title.replace('💭', '')
    title = title.replace('🌏', '')
    title = title.replace('🤙', '')
    title = title.replace('🧐', '')
    title = title.replace('🏅', '')
    title = title.replace('🏔', '')
    title = title.replace('👟', '')
    title = title.replace('▬', '')
    title = title.replace('🏎', '')
    title = title.replace('🏃', '')
    title = title.replace('🎤', '')
    title = title.replace('⠗', '')
    title = title.replace('😎', '')
    title = title.replace('🧺', '')
    title = title.replace('🎪', '')
    title = title.replace('🎈', '')
    title = title.replace('🤔', '')
    title = title.replace('☃️', '')
    title = title.replace('🟦', '')
    title = title.replace('🧩', '')
    title = title.replace('💃', '')
    title = title.replace('🖐', '')
    title = title.replace('✨', '')
    title = title.replace('–', '_')
    title = title.replace('-', '_')
    
    # Clean up special chars
    title = re.sub(r'[^\w\s\-_]', '', title)
    
    # Spaces to underscores
    title = re.sub(r'\s+', '_', title)
    
    # Multiple underscores to single
    title = re.sub(r'_+', '_', title)
    
    # Remove leading/trailing underscores
    title = title.strip('_')
    
    return title


def generate_standardized_name(old_filename: str, season: int, episode: int) -> str:
    """Generate standardized filename."""
    # Extract title part by removing season/episode patterns
    title_part = re.sub(r'^[Ss]\d+[Ee]\d+[_\-]?', '', old_filename)
    
    # Also remove wrong-order patterns (Title_S3E14)
    title_part = re.sub(r'[_\-]?[Ss]\d+[Ee]\d+(?!.*[Ss]\d+[Ee]\d+)', '', title_part)
    
    # Remove .mp4 extension for processing
    title_part = re.sub(r'\.mp4$', '', title_part)
    
    # Clean the title
    title_part = clean_title(title_part)
    
    # Generate new name
    if season == 0:
        return f"S00E{episode:02d}_{title_part}.mp4"
    else:
        return f"S{season:02d}E{episode:02d}_{title_part}.mp4"


def analyze_file(file_path: Path) -> Optional[Tuple[Path, Path, str]]:
    """
    Analyze a file and determine if renaming is needed.
    Returns: (old_path, new_path, reason) or None if no change needed
    """
    filename = file_path.name
    
    # Skip non-mp4 files
    if not filename.endswith('.mp4'):
        return None
    
    # Skip partial downloads
    if '.part' in filename or '.ytdl' in filename:
        return None
    
    # Check if already in correct format: S##E##_CleanTitle.mp4
    if re.match(r'^S\d{2}E\d{2}_[^_][^\\/]*\.mp4$', filename):
        # Further check: title should not contain special patterns
        title_match = re.search(r'^S\d{2}E\d{2}_(.+)\.mp4$', filename)
        if title_match:
            title = title_match.group(1)
            # If title looks clean (no special chars, no long suffixes), it's valid
            if not re.search(r'[｜｜]\s*Full Episode', title) and len(title) < 80:
                return None
    
    # Extract info
    season, episode, _ = extract_info_from_filename(filename)
    
    if season is None or episode is None:
        return None
    
    # Generate new name
    new_filename = generate_standardized_name(filename, season, episode)
    new_path = file_path.parent / new_filename
    
    # If new name is same as old, no change needed
    if new_filename == filename:
        return None
    
    reason = f"Format fix"
    
    return file_path, new_path, reason


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Standardize Numberblocks filenames')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually perform the renames (default is preview mode)')
    args = parser.parse_args()
    
    downloads_dir = Path('downloads')
    
    print("=" * 70)
    print("Numberblocks Filename Standardization")
    print("=" * 70)
    
    # Find all files needing rename
    renames = []
    
    for season_dir in sorted(downloads_dir.glob('*_HD')):
        print(f"\nAnalyzing {season_dir.name}...")
        
        for file_path in sorted(season_dir.glob('*.mp4')):
            result = analyze_file(file_path)
            if result:
                old_path, new_path, reason = result
                renames.append((old_path, new_path))
                print(f"  {old_path.name[:50]}...")
                print(f"    -> {new_path.name[:50]}...")
    
    if not renames:
        print("\n✓ All files already have correct naming!")
        return 0
    
    print(f"\n{'=' * 70}")
    print(f"Files to rename: {len(renames)}")
    print(f"{'=' * 70}")
    
    if not args.execute:
        print("\nPreview mode - no changes made.")
        print("Run with --execute to perform actual renaming.")
        return 0
    
    # Execute mode
    print("\nExecuting renames...")
    success = 0
    failed = 0
    
    for old_path, new_path in renames:
        try:
            shutil.move(str(old_path), str(new_path))
            print(f"  ✓ {old_path.name[:40]}...")
            success += 1
        except Exception as e:
            print(f"  ✗ Failed: {old_path.name[:40]}... - {e}")
            failed += 1
    
    print(f"\n{'=' * 70}")
    print("Rename Summary")
    print(f"{'=' * 70}")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Total:   {success + failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
