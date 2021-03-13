# avutil

[![Release](https://img.shields.io/pypi/v/avutil?color=%2366CCFF&label=release)](https://pypi.org/project/avutil/)

Provide some useful utils for *tidying up* your personal video folder.
Data source from *LIBRARY* or *BUS*.

- Extract designatio
- Search folder (recursively)
- Pull & save video info (title, actors etc.)
- Download cover image
- Rename video file

![gjf](https://github.com/Lqlsoftware/avutil/blob/main/doc/demo.gif)

## Environment

    Python >= 3.4
    BeautifulSoup4 >= 4.7.0
    requests >= 2.21.0

## Install

```sh
pip install avutil
```

## Usage

```sh
$ tidyup -h
```

Tidy up current dir

```sh
$ tidyup
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
videos = avutil.Search_folder(folder, media_suffix={"mp4", "wmv", "avi", "mkv"})
```

Pull video info from *LIBRARY* by default & download cover image
```python
for video in videos:
    # Pull video info
    video.pull_info()

    # Download cover image (as video.title + .jpg)
    video.download_cover()
```

It's okey using *BUS*
```python
for video in videos:
    # Pull video info
    video.pull_info(source=avutil.Bus())
```

Save video info as .nfo file
```python
for video in videos:
    # Save video info
    video.save_info()
```

Tidy up!

```python
    # Tidy up (rename to video.designatio + video.actors)
    video.rename()
```

## Proxy

Proxy is supported in avutil in two ways, you can define a global bash variable (eg. http proxy):
```shell
$ export HTTP_PROXY="http://127.0.0.1:1087"
```

Or you can pass http-proxy in code
```python
video.pull_info(use_proxy=True, http_proxy="http://127.0.0.1:1087")
video.download_cover(use_proxy=True, http_proxy="http://127.0.0.1:1087")
```
