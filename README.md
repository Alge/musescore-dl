# ms-downloader
Command-line tool for downloading musescore PDFs and midi files. Old sheets don't have any SVG files available, so they will be downloaded with lower quality png files.

Usage:
```bash
./musescore-dl.py https://musescore.com/nicolas/scores/539 --pdf --midi -o "Mozart_Sonate_in_C"
```

Requires python > 3.6
