import os
import io
import re
import requests
import xml.etree.ElementTree as ET
import PIL.Image

from avutil.info import VideoInfo
# from avutil import VideoInfo
from avutil.encoder import NFOEncoder
from avutil.encoder import VSMETAEncoder
from avutil.source import Library
from avutil.source import Bus


def strip(string):
    return re.sub(r"\/|\?|\*|\:|\||\\|\<|\>", "", string)


class File:
    path = ""
    dir = ""
    name = ""
    ext = ""

    def __init__(self, file_path):
        self.path = file_path
        self.dir = os.path.dirname(file_path)
        self.name = os.path.basename(file_path)
        self.ext = os.path.splitext(file_path)[1]

    def __str__(self):
        return self.path


class Video:
    ''' Descriptor of video:

        Provide following operations:
            pull_info(): Pull video info from source
            download_cover(): Download cover
            rename(): Rename as designatio + title
            save_info(): Save info to file
    '''

    def __init__(self, designatio, file_paths=[]):
        self.info = VideoInfo(designatio)
        self.is_updated = False
        # File attributes
        self.slices = len(file_paths)
        self.file_path = []
        self.dst_path = []
        file_paths = sorted(file_paths)
        for path in file_paths:
            self.file_path.append(File(path))
            self.info.subtitle = os.path.splitext(
                path)[0].upper().endswith("C")

    def __str__(self):
        ret = "[文件 {0}]".format(
            " ".join([str(file) for file in self.file_path])
        )
        if not self.is_updated:
            return ret
        else:
            return ret + str(self.info)

    def __gen_file_name(self):
        if len(self.info.title.encode()) > 200:
            if len(self.info.cast) == 1:
                overflow = 200 - len(self.info.cast[0].encode())
                return "{:}.. {:}".format(self.info.title[:overflow // 3], self.info.cast[0])
            else:
                overflow = 200
                return self.info.title[:overflow // 3]
        else:
            return strip(self.info.title)

    def pull_info(self, source=Library, http_proxy=""):
        ''' Pull video details by designatio from source. 

            source is set to Library by default
            http_proxy is set to "" by default
        '''
        source = source(http_proxy=http_proxy)
        self.video_url = source.base_url + source.search_prefix + self.info.designatio
        try:
            attrs = source.Get(self.info.designatio)
            for name, value in attrs.items():
                self.info.__setattr__(name, value)
        except Exception as e:
            print("Mata-data not found or network error, please try enable proxy:")
            print("    Exception: ", str(e))
            print("    ", " ".join([str(file) for file in self.file_path]))
            return
        if self.info.subtitle:
            self.info.genres.append("中文字幕")

        # Join path (slices)
        if self.slices > 1:
            for idx in range(self.slices):
                self.dst_path.append("{:} {:}".format(
                    self.__gen_file_name(),
                    chr(ord("A") + idx)
                ))
        else:
            self.dst_path.append(self.__gen_file_name())

        self.is_updated = True

    def download_cover(self, dst_dir=None, http_proxy="", with_poster=False):
        ''' download cover of video title

            dst_dir will be orignal file_dir by default
        '''

        # Need pulling info
        if not self.is_updated:
            return False

        # Download image
        dw_bytes = io.BytesIO()
        r = requests.get(self.info.cover_url, stream=True,
                         proxies={"http": http_proxy})
        if r.status_code == 200:
            for chunk in r:
                dw_bytes.write(chunk)

        # Cut Poster
        img_bytes = io.BytesIO()
        with PIL.Image.open(io.BytesIO(dw_bytes.getvalue())) as img:
            img.crop((img.width / 1.9, 0, img.width, img.height)
                     ).save(img_bytes, format='jpeg')

        # Update fanart, thumb
        self.info.fanart = dw_bytes.getvalue()
        self.info.thumb = dw_bytes.getvalue()
        self.info.poster = img_bytes.getvalue()

        # Save as jpeg file
        #   User specify download dir
        if dst_dir is None:
            dst_dir = "./"
        if not os.path.exists(dst_dir):
            return False

        #   Fanart
        self.info.fanart_path = os.path.join(
            dst_dir, self.__gen_file_name() + "-fanart.jpg")
        if not os.path.exists(self.info.fanart_path):
            with open(self.info.fanart_path, "+wb") as f:
                f.write(self.info.fanart)

        if with_poster:
            #   Thumb
            self.info.thumb_path = os.path.join(
                dst_dir, self.__gen_file_name() + "-thumb.jpg")
            if not os.path.exists(self.info.thumb_path):
                with open(self.info.thumb_path, "+wb") as f:
                    f.write(self.info.thumb)

            #   Poster
            self.info.poster_path = os.path.join(
                dst_dir, self.__gen_file_name() + "-poster.jpg")
            if not os.path.exists(self.info.poster_path):
                with open(self.info.poster_path, "+wb") as f:
                    f.write(self.info.poster)
        else:
            self.info.thumb_path = self.info.fanart_path
            self.info.poster_path = self.info.fanart_path

        return True

    def rename(self, dst_dir=None):
        ''' rename video files by title

            dst_dir will be orignal file_dir by default
        '''

        # Need pulling info
        if not self.is_updated:
            return False

        # User specify rename dir
        if dst_dir is None:
            dst_dir = "./"

        # Join path (slices)
        dsts = []
        for idx in range(self.slices):
            if len(self.dst_path[idx]) == 0:
                return False
            dsts.append(os.path.join(
                dst_dir, self.dst_path[idx] + self.file_path[idx].ext))

        # Already exist or rename dir not exist
        if not os.path.exists(dst_dir):
            return False
        for idx in range(self.slices):
            if os.path.exists(dsts[idx]):
                return False

        # Rename
        for idx in range(self.slices):
            os.rename(self.file_path[idx].path, dsts[idx])
            self.file_path[idx] = File(dsts[idx])
        return True

    def save_info(self, dst_dir=None, encoder=NFOEncoder):
        ''' Save video info as title.nfo

            dst_dir will be orignal file_dir by default
        '''

        # Need pulling info
        if not self.is_updated:
            return False

        # User specify rename dir
        if dst_dir is None:
            dst_dir = "./"

        # Join path (slices)
        dsts = []
        for idx in range(self.slices):
            if encoder == VSMETAEncoder:
                dsts.append(os.path.join(
                    dst_dir, self.dst_path[idx] + self.file_path[idx].ext + encoder.ext))
            else:
                dsts.append(os.path.join(
                    dst_dir, self.dst_path[idx] + encoder.ext))

        # Already exist or dst dir not exist
        if not os.path.exists(dst_dir):
            return False

        # Encode by selected encoder
        encoded_bytes = encoder().encode(self.info.todict())

        for idx in range(self.slices):
            if not os.path.exists(dsts[idx]):
                with open(dsts[idx], "+wb") as f:
                    f.write(encoded_bytes)
        return True
