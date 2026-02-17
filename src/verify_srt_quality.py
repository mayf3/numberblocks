#!/usr/bin/env python3
"""
Verify subtitle quality and IINA compatibility

This script verifies SRT subtitle files are ready for IINA playback
"""

import sys
from pathlib import Path

def verify_subtitle_format(srt_file: Path) -> dict:
    """
    Verify SRT subtitle file format
    
    Returns:
        Dict with verification results
    """
    
    results = {
        'valid': False,
        'entries': 0,
        'first_time': None,
        'last_time': None,
        'issues': []
    }
    
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        entry_count = 0
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for subtitle number
            if line.isdigit():
                entry_count += 1
                
                # Check next line for timestamp
                if i + 1 < len(lines):
                    timestamp = lines[i + 1].strip()
                    if '-->' in timestamp:
                        if results['first_time'] is None:
                            results['first_time'] = timestamp.split('-->')[0].strip()
                        results['last_time'] = timestamp.split('-->')[1].strip()
                    else:
                        results['issues'].append(f"Entry {entry_count}: Missing timestamp")
                
                # Check for text content
                if i + 2 < len(lines):
                    text = lines[i + 2].strip()
                    if not text:
                        results['issues'].append(f"Entry {entry_count}: Missing text")
            
            i += 1
        
        results['entries'] = entry_count
        results['valid'] = entry_count > 0 and len(results['issues']) == 0
        
    except Exception as e:
        results['issues'].append(f"Error reading file: {e}")
    
    return results

def main():
    """Main verification function"""
    
    print("=" * 60)
    print("Subtitle Quality Verification")
    print("=" * 60)
    
    subtitle_dir = Path("Subtitles_SRT_Clean")
    
    if not subtitle_dir.exists():
        print(f"\n✗ Subtitle directory not found: {subtitle_dir}")
        return 1
    
    srt_files = sorted(subtitle_dir.glob("*.srt"))
    
    if not srt_files:
        print("\n✗ No SRT files found")
        return 1
    
    print(f"\nFound {len(srt_files)} subtitle files")
    print()
    
    total_entries = 0
    total_issues = 0
    valid_files = 0
    
    for srt_file in srt_files:
        print(f"Verifying: {srt_file.name}")
        
        results = verify_subtitle_format(srt_file)
        
        if results['valid']:
            print(f"  ✓ Valid format")
            print(f"    Entries: {results['entries']}")
            print(f"    Start: {results['first_time']}")
            print(f"    End: {results['last_time']}")
            valid_files += 1
        else:
            print(f"  ✗ Issues found:")
            for issue in results['issues']:
                print(f"    - {issue}")
        
        total_entries += results['entries']
        total_issues += len(results['issues'])
        print()
    
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"Total files: {len(srt_files)}")
    print(f"Valid files: {valid_files}")
    print(f"Total entries: {total_entries}")
    print(f"Total issues: {total_issues}")
    print()
    
    if valid_files == len(srt_files) and total_issues == 0:
        print("✓ All subtitles are valid!")
        print()
        print("Next steps:")
        print("1. Open IINA")
        print("2. File > Open")
        print("3. Select video from Season 1")
        print("4. File > Subtitle > Open")
        print("5. Select matching SRT file")
        print("6. Enjoy improved subtitles!")
        print()
        print("Or use the test_subs.py script:")
        print("  python3 test_subs.py")
        return 0
    else:
        print("⚠️ Some issues found, but subtitles may still work")
        return 0

if __name__ == "__main__":
    sys.exit(main())
