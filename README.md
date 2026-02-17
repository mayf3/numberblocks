# Numberblocks HD Download Project

Consolidated 1080p HD episodes of Numberblocks from YouTube.

---

## Project Structure

```
numberblocks/
├── downloads/          # 1080p HD video files organized by season (gitignored)
│   ├── Season_1_HD/
│   ├── Season_2_HD/
│   ├── Season_3_HD/
│   ├── Season_5_HD/
│   ├── Season_7_HD/
│   ├── Season_8_HD/
│   └── Specials_HD/
├── src/
│   ├── download.py         # Main downloader (simplified, working)
│   └── fetch_playlists.py  # Playlist metadata fetcher
├── playlists.json          # Episode metadata and URLs
└── README.md               # This file
```

---

## Quick Start

### 1. Update Playlists (Optional)
```bash
python3 src/fetch_playlists.py
```

### 2. Download Episodes
```bash
python3 src/download.py
```

This will:
- Read `playlists.json` for episode URLs
- Download 1080p videos with English subtitles
- Save to `downloads/Season_X_HD/` with naming format `S##E##_Title.mp4`
- Skip already downloaded episodes

---

## Stats

- **Total Episodes:** 129 files (after deduplication and standardization)
- **Seasons:** 6 seasons + Specials
  - Season 1: 15 episodes
  - Season 2: 14 episodes
  - Season 3: 31 episodes
  - Season 5: 30 episodes
  - Season 7: 15 episodes
  - Season 8: 15 episodes
  - Specials: 9 episodes
- **Quality:** 1080p HD
- **Size:** ~5.9GB
- **Naming:** Standardized to `S##E##_Title.mp4` format

---

## License

For personal learning only. Please support official channels:
- [Numberblocks Official](https://www.blocksuniverse.tv/numberblocks/home)
- [BBC iPlayer](https://www.bbc.co.uk/iplayer)
- [YouTube Official](https://www.youtube.com/@Numberblocks)
