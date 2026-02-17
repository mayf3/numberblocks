#!/usr/bin/env python3
"""
Extract and convert YouTube subtitles to clean SRT format

This script extracts embedded subtitles from Numberblocks videos,
converts VTT to SRT format, and cleans up timing issues.
"""

import sys
import subprocess
from pathlib import Path
import re

def extract_subtitles(video_path: Path, output_dir: Path) -> Path | None:
    """
    Extract embedded subtitles from video file
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save extracted subtitles
    
    Returns:
        Path to extracted subtitle file
    """
    
    output_srt = output_dir / f"{video_path.stem}.srt"
    
    print(f"Extracting subtitles from: {video_path.name}")
    print(f"Output: {output_srt}")
    
    # Use ffmpeg to extract subtitles
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-map", "0:s:0",  # First subtitle track
        "-c:s", "srt",
        str(output_srt),
        "-y"  # Overwrite
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Subtitles extracted: {output_srt}")
            return output_srt
        else:
            # Try alternative method
            print(f"  ⚠️ Direct extraction failed, trying conversion...")
            return extract_and_convert(video_path, output_dir)
    
    except FileNotFoundError:
        print(f"  ✗ ffmpeg not found")
        print(f"  Install: brew install ffmpeg")
        return None

def extract_and_convert(video_path: Path, output_dir: Path) -> Path | None:
    """
    Extract and convert VTT to SRT
    """
    
    # First extract VTT
    output_vtt = output_dir / f"{video_path.stem}.vtt"
    
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-map", "0:s:0",
        "-c:s", "webvtt",
        str(output_vtt),
        "-y"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ✗ Extraction failed")
        return None
    
    # Convert VTT to SRT
    return vtt_to_srt(output_vtt, output_dir)

def vtt_to_srt(vtt_path: Path, output_dir: Path) -> Path:
    """
    Convert VTT format to SRT format
    """
    
    srt_path = output_dir / f"{vtt_path.stem}.srt"
    
    print(f"Converting {vtt_path.name} to SRT...")
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove VTT header
    content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    
    # Remove VTT timestamp cues
    content = re.sub(r'Kind: captions.*?\n', '', content)
    content = re.sub(r'Language: en.*?\n', '', content)
    
    # Parse and convert timestamps
    lines = content.split('\n')
    srt_lines = []
    counter = 1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for timestamp lines
        if '-->' in line:
            # Convert timestamp format
            timestamp = line.replace('.', ',')  # VTT uses ., SRT uses ,
            timestamp = re.sub(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', r'\1:\2:\3,\4', timestamp)
            
            srt_lines.append(str(counter))
            srt_lines.append(timestamp)
            
            # Add subtitle text (skip empty lines)
            i += 1
            while i < len(lines) and lines[i].strip() not in ['', '-->']:
                text_line = lines[i].strip()
                
                # Remove VTT color tags
                text_line = re.sub(r'<c\.color[^>]*>', '', text_line)
                text_line = re.sub(r'<c>', '', text_line)
                text_line = re.sub(r'</c>', '', text_line)
                
                # Remove position tags
                text_line = re.sub(r'<[^>]+>', '', text_line)
                
                if text_line:
                    srt_lines.append(text_line)
                i += 1
            
            srt_lines.append('')
            counter += 1
        else:
            i += 1
    
    # Write SRT file
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_lines))
    
    print(f"  ✓ Converted: {srt_path}")
    
    # Clean up VTT file
    vtt_path.unlink()
    
    return srt_path

def process_season(season_dir: Path) -> int:
    """
    Process all videos in a season directory
    
    Returns:
        Number of videos processed
    """
    
    output_dir = Path("Subtitles_SRT_Clean")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nProcessing Season: {season_dir}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    video_files = sorted(season_dir.glob("*.mp4"))
    
    if not video_files:
        print("No MP4 files found")
        return 0
    
    print(f"Found {len(video_files)} video files")
    
    success = 0
    failed = 0
    
    for video in video_files:
        result = extract_subtitles(video, output_dir)
        
        if result:
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"Success: {success}/{len(video_files)}")
    print(f"Failed: {failed}/{len(video_files)}")
    
    if success > 0:
        print(f"\n✓ Subtitles ready in: {output_dir}")
    
    return success

def main():
    """Main function"""
    
    print("=" * 60)
    print("Numberblocks Subtitle Extractor")
    print("=" * 60)
    
    # Check for ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"],
                     capture_output=True, check=True)
        print("✓ ffmpeg found")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("✗ ffmpeg not found")
        print("\nInstall ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        return 1
    
    # Get season from command line or default to Season 1
    season_arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    season_num = int(season_arg)
    season_1 = Path(f"Season {season_num}")
    
    if not season_1.exists():
        print(f"\n✗ Season 1 directory not found: {season_1}")
        return 1
    
    count = process_season(season_1)
    
    if count >= 10:
        print("\n✓ SUCCESS: Subtitles extracted and cleaned")
        return 0
    else:
        print(f"\n⚠️ Only {count} subtitles extracted")
        return 1

if __name__ == "__main__":
    sys.exit(main())
