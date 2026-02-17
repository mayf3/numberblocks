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
│       └── peppa_pig.yaml       # Example: Peppa Pig template
├── src/
│   ├── download.py              # Generic downloader (supports any series)
│   └── fetch_playlists.py       # Fetch metadata from YouTube
├── downloads/                   # Downloaded videos (gitignored)
│   └── Season_X_HD/
├── numberblocks_playlists.json  # Fetched metadata
└── numberblocks_downloaded.txt  # Download tracking (gitignored)
```

---

## Quick Start

### 1. Setup

Install dependencies:
```bash
pip install pyyaml yt-dlp
```

### 2. Fetch Playlists

For Numberblocks (default):
```bash
python3 src/fetch_playlists.py numberblocks
```

For other series (create config first):
```bash
python3 src/fetch_playlists.py peppa_pig
```

### 3. Download Episodes

```bash
# Download Numberblocks
python3 src/download.py numberblocks

# Skip confirmation prompt
python3 src/download.py numberblocks --yes

# Download to custom directory
python3 src/download.py numberblocks --download-dir /path/to/videos
```

---

## Adding a New Series

1. **Create config file** in `config/series/<series_name>.yaml`:

```yaml
series_name: "Peppa Pig"
description: "British preschool animated series"

# Naming pattern for files
naming_pattern: "S{season:02d}E{episode:02d}_{title}.mp4"
directory_pattern: "Season_{season}_HD"

# Video quality
quality: 1080

# Subtitles
subtitles:
  enabled: true
  lang: "en"
  embed: true

# YouTube playlist IDs
seasons:
  Season 1: PLxxxxx
  Season 2: PLxxxxx
```

2. **Fetch metadata**:
```bash
python3 src/fetch_playlists.py peppa_pig
```

3. **Download**:
```bash
python3 src/download.py peppa_pig
```

---

## Configuration Options

### Naming Patterns

Available variables:
- `{season}` - season number (1, 2, 3...)
- `{season:02d}` - season with leading zero (01, 02...)
- `{episode}` - episode number
- `{episode:02d}` - episode with leading zero
- `{title}` - video title (sanitized)

### Directory Patterns

- `{series_name}` - series name
- `{season}` - season number
- `{season_name}` - full season name from config

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
