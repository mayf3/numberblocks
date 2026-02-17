# Numberblocks HD Download Project

Consolidated 1080p HD episodes of Numberblocks from YouTube.

---

## Project Structure

```
numberblocks/
├── downloads/          # 1080p HD video files (gitignored)
├── src/
│   ├── downloaders/    # Core downloader: download_all_videos.py
│   ├── extractors/    # URL extraction and subtitle tools
│   └── validators/    # Verification scripts
├── scripts/            # Utility scripts
├── subtitles/          # Subtitles (vtt, srt)
├── data/              # JSON configs, logs, reports
├── archive/           # Historical scripts (archived)
└── docs/              # Documentation
```

---

## Quick Start

```bash
# Download all episodes
python3 src/downloaders/download_all_videos.py

# Verify downloads
python3 src/downloaders/validate_downloads.py
```

---

## Stats

- **Total Episodes:** 105 (103 available, 2 unavailable)
- **Quality:** 1080p HD
- **Size:** ~4.5GB

---

## License

For personal learning only. Please support official channels:
- [Numberblocks Official](https://www.blocksuniverse.tv/numberblocks/home)
- [BBC iPlayer](https://www.bbc.co.uk/iplayer)
- [YouTube Official](https://www.youtube.com/@Numberblocks)
