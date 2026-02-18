# YouTube Series Downloader

Generic tool for downloading educational series from YouTube in 1080p HD.
Supports multiple series via YAML configuration files.

**Included Example:** Numberblocks - 129 episodes (6 seasons + Specials)

---

## Project Structure

```
├── config/
│   └── series/
│       ├── numberblocks.yaml    # Numberblocks configuration
│       └── peppa_pig.yaml       # TEST config - for development only
├── src/
│   └── download.py              # Generic downloader
└── downloads/                   # Downloaded videos (gitignored)
    └── Season_X_HD/
```

---

## Quick Start

### 1. Setup

```bash
pip install pyyaml yt-dlp
```

### 2. Download Episodes

```bash
python3 src/download.py numberblocks

python3 src/download.py numberblocks --yes

python3 src/download.py numberblocks --download-dir /path/to/videos
```

---

## Adding a New Series

1. **Create config file** in `config/series/<series_name>.yaml`:

```yaml
series_name: "My Series"
description: "Series description"

naming_pattern: "S{season:02d}E{episode:02d}_{title}.mp4"
directory_pattern: "Season_{season}_HD"

quality: 1080

subtitles:
  enabled: true
  lang: "en"
  embed: true

episodes:
  Season 1:
    - title: "S01E01 Episode Title"
      id: "YOUTUBE_VIDEO_ID"
    - title: "S01E02 Another Episode"
      id: "YOUTUBE_VIDEO_ID"
```

2. **Download**:
```bash
python3 src/download.py my_series
```

---

## Configuration Options

### Naming Patterns

- `{season}` - season number (1, 2, 3...)
- `{season:02d}` - season with leading zero (01, 02...)
- `{episode}` - episode number
- `{episode:02d}` - episode with leading zero
- `{title}` - video title (sanitized)

### Directory Patterns

- `{series_name}` - series name
- `{season}` - season number

---

## Numberblocks Stats

- **Total Episodes:** 129 files (6 seasons + Specials)
- **Seasons:** 6 seasons + Specials
  - Season 1: 15 episodes
  - Season 2: 15 episodes
  - Season 3: 30 episodes
  - Season 5: 30 episodes
  - Season 7: 15 episodes
  - Season 8: 15 episodes
  - Specials: 9 episodes
- **Quality:** 1080p HD
- **Size:** ~5.9GB
- **Naming:** Standardized to `S##E##_Title.mp4` format

---

## License

For personal learning only. Please support official channels.

**Numberblocks:**
- [Numberblocks Official](https://www.blocksuniverse.tv/numberblocks/home)
- [BBC iPlayer](https://www.bbc.co.uk/iplayer)
- [YouTube Official](https://www.youtube.com/@Numberblocks)

**Peppa Pig:**
- [Official Website](https://www.peppapig.com)
- [YouTube Channel](https://www.youtube.com/@PeppaPig)
