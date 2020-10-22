# AV Utils

Provide some useful utils for tidying up your personal video folder

- Extract designatio
- Search folder (recursively)
- Pull video info (title, actors etc.)
- Download cover image
- Rename video file

## Environment

    Python >= 3.4
    BeautifulSoup4 >= 4.7.0

## Install

```sh
pip install avutil
```

## Usage

```sh
# tidyup -h
```

Tidy up current dir

```sh
# tidyup
```

## Usage in Python script

Import avutil:
```python
import avutil
```

Search folder recursively to find videos:
```python
folder = "StudyResource"
videos = avutil.Search_folder(folder)
```

Or you can specify the extension type of video
```python
videos = Search_folder(folder, media_suffix={"mp4", "wmv", "avi", "mkv"})
```

Pull video info & download cover image
```python
for video in videos:
    # Pull video info
    video.pull_info()
    print(video)

    # Download cover image (as video.title + .jpg)
    video.download_cover()
```

(Or proxy supported!)
```python
for video in videos:
    # Pull video info using proxy
    video.pull_info(use_proxy=True, http_proxy="http://127.0.0.1:1087")
    print(video)
    # Download cover image using proxy (as video.title + .jpg)
    video.download_cover(use_proxy=True, http_proxy="http://127.0.0.1:1087")
```

Tidy up!

```python
    # Tidy up (rename to video.title)
    video.rename()
```