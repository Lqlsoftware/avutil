# avutil

[![Release](https://img.shields.io/pypi/v/avutil?color=%2366CCFF&label=release)](https://pypi.org/project/avutil/)

Provide some useful util functions (and a poweful tool `tidyup`) for *tidying up* your personal video folder.
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

## Usage of tidyup

```sh
$ tidyup -h
usage: tidyup [-h] [-r] [-i IN] [-o OUT] [-p PROXY] [-s SOURCE] [-t THREAD] [-e ENCODER] [--with-poster]

Tidy up your personal video dir

optional arguments:
  -h, --help            show this help message and exit
  -r                    search dir recursively
  -i IN, --in IN        video input dir
  -o OUT, --out OUT     video output dir
  -p PROXY, --proxy PROXY
                        http proxy address
  -s SOURCE, --source SOURCE
                        data source of video info, 'library' or 'bus'
  -t THREAD, --thread THREAD
                        threads num, use multi-threads to download info & images
  -e ENCODER, --encoder ENCODER
                        encoder of meta-data, 'nfo'(default) or 'vsmeta'
  --with-poster         save poster
```

Tidy up current dir

```sh
$ tidyup
```

## Python script usage

Import avutil:
```python
import avutil
```

Search folder recursively to find videos:
```python
folder = "StudyResource"
videos = avutil.Search_folder(folder)
# videos: map { designatio -> [ slice_paths ] }
```

Or you can specify the extension type of video
```python
videos = avutil.Search_folder(folder, media_suffix={".mp4", ".wmv", ".avi", ".mkv"})
```

Pull video info from *LIBRARY* by default & download cover image
```python
for designatio, file_paths in videos.items():
    video = avutil.Video(designatio, file_paths)

    # Pull video info
    video.pull_info()

    # Download cover image (as video.title + .jpg)
    video.download_cover()
```

It's okey using *BUS*
```python
    # Pull video info
    video.pull_info(source=avutil.Bus)
```

Save video info as .nfo file
```python
    # Save video info
    video.save_info()
```

Tidy up!

```python
    # Tidy up (rename to video.designatio + video.actors)
    video.rename()
```

## Proxy

Proxy is supported in avutil in two ways, you can either pass http-proxy in code
```python
video.pull_info(http_proxy="http://127.0.0.1:1087")
video.download_cover(http_proxy="http://127.0.0.1:1087")
```
Or define a global bash variable (eg. http proxy):
```shell
$ export HTTP_PROXY="http://127.0.0.1:1087"
```
