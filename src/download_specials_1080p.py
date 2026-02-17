#!/usr/bin/env python3
"""Download Specials in 1080p with subtitles."""
import subprocess
from pathlib import Path

SPECIALS = [
    ("01", "Treasure_Of_Hexagon_Island", "SVWo8e0E0ks"),
    ("02", "Twelve_Days_Of_Christmas", "5j8zQFn9hgE"),
    ("03", "About_Time", "oyaDS_C3mOQ"),
    ("04", "Double_Back", "_ot3JWCSyBw"),
]

def download_special(num, title, video_id):
    output = Path(f"downloads/Specials_HD/SP{num}_{title}.mp4")
    if output.exists():
        output.unlink()
    cmd = [
        "python3", "-m", "yt_dlp",
        "--remote-components", "ejs:github",
        "-f", "best[height<=1080]",
        "--write-sub", "--sub-lang", "en",
        "--embed-subs",
        "-o", str(output),
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    print(f"Downloading SP{num}: {title}")
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    Path("downloads/Specials_HD").mkdir(parents=True, exist_ok=True)
    for num, title, video_id in SPECIALS:
        success = download_special(num, title, video_id)
        print(f"  {'✓' if success else '✗'}")
