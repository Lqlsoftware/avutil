import os
import shutil
import re
import requests
import xml.etree.ElementTree as ET
import PIL

from avutil.bus import Bus
from avutil.library import Library


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
    ''' Describe details of an video which includes:

        'designatio' 'title' 'cover_url' 'date' 'length'
        'director' 'maker' 'label' 'genres' 'cast'
    '''

    def __init__(self, designatio, file_paths=[]):
        self.is_updated = False
        # File attributes
        self.slices = len(file_paths)
        self.file_path = []
        self.dst_path = []
        self.fanart = []
        self.poster = []
        self.thumb = []
        file_paths = sorted(file_paths)
        for path in file_paths:
            self.file_path.append(File(path))
            self.subtitle = os.path.splitext(path)[0].endswith("C")

        # Video attributes
        self.designatio = designatio.upper()
        self.title = ""
        self.outline = ""
        self.subtitle = False
        self.cover_url = ""
        self.video_url = ""
        self.date = ""
        self.length = ""
        self.director = ""
        self.maker = ""
        self.label = ""
        self.review = ""
        self.series = []
        self.genres = []
        self.cast = []

    def __str__(self):
        ret = "[文件 {0}]".format(
            " ".join([str(file) for file in self.file_path])
        )
        if not self.is_updated:
            return ret
        else:
            return ret + '''\n
    标题\t{0.title}
    番号\t{0.designatio}
    发行日期\t{0.date}
    影片长度\t{0.length}
    导演\t{0.director}
    制作商\t{0.maker}
    发行商\t{0.label}
    评分\t{0.review}
    系列\t{0.series}
    类别\t{0.genres}
    演员\t{0.cast}
    简介\t{0.outline}\n'''.format(self)

    def __gen_file_name(self):
        if len(self.title.encode()) > 220:
            if len(self.cast) == 1:
                overflow = 227 - len(self.title.encode()) - len(self.cast[0])
                return "{:}.. {:}".format(self.title[:overflow], self.cast[0])
            else:
                overflow = 230 - len(self.title.encode())
                return self.title[:overflow]

        else:
            return strip(self.title)

    def pull_info(self, source=Library, http_proxy=""):
        ''' Pull video details by designatio from source. 

            source is set to Library() by default

            http_proxy is set to "" by default
        '''
        source = source(http_proxy=http_proxy)
        self.video_url = source.base_url + source.search_prefix + self.designatio
        try:
            attrs = source.Get(self.designatio)
            for name, value in attrs.items():
                self.__setattr__(name, value)
        except Exception:
            print(
                "Video not recruited or require proxy: ",
                " ".join([str(file) for file in self.file_path])
            )
            return
        if self.subtitle:
            self.genres.append("中文字幕")

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

        # User specify download dir
        if dst_dir is None:
            dst_dir = "./"

        # Join path
        dsts = []
        for idx in range(self.slices):
            dsts.append(os.path.join(
                dst_dir, self.dst_path[idx] + "-fanart.jpg"))
        self.fanart = dsts

        # Already exist or download dir not exist
        if not os.path.exists(dst_dir):
            return False
        if not os.path.exists(dsts[0]):
            # Proxy
            r = requests.get(self.cover_url, stream=True,
                             proxies={"http": http_proxy})

            # Download
            if r.status_code == 200:
                with open(dsts[0], 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

        # Copy for each slice
        for idx in range(1, self.slices):
            if not os.path.exists(dsts[idx]):
                shutil.copyfile(dsts[0], dsts[idx])

        # Poster cut
        self.poster = [e for e in self.fanart]
        self.thumb = [e for e in self.fanart]
        if with_poster:
            try:
                for idx in range(self.slices):
                    thumb_file = os.path.join(
                        dst_dir, self.dst_path[idx] + "-thumb.jpg")
                    if not os.path.exists(thumb_file):
                        shutil.copyfile(dsts[0], thumb_file)
                        self.thumb[idx] = thumb_file

                poster_file = os.path.join(
                    dst_dir, self.dst_path[0] + "-poster.jpg")
                if not os.path.exists(poster_file):
                    img = PIL.Image.open(dsts[0])
                    img.crop((img.width / 1.9, 0, img.width,
                             img.height)).save(poster_file)
                    self.poster[0] = poster_file

                for idx in range(1, self.slices):
                    poster_file = os.path.join(
                        dst_dir, self.dst_path[idx] + "-poster.jpg")
                    if not os.path.exists(poster_file):
                        shutil.copyfile(self.poster[0], poster_file)
                        self.poster[idx] = poster_file
            except:
                pass
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

    def save_info(self, dst_dir=None):
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
            dsts.append(os.path.join(dst_dir, self.dst_path[idx] + ".nfo"))

        # Already exist or dst dir not exist
        if not os.path.exists(dst_dir):
            return False

        nfo_movie = ET.Element("movie")
        ET.SubElement(nfo_movie, "title").text = self.title
        ET.SubElement(nfo_movie, "set")
        ET.SubElement(nfo_movie, "studio").text = self.maker
        ET.SubElement(nfo_movie, "year").text = self.date[:4]
        ET.SubElement(nfo_movie, "outline").text = self.outline
        ET.SubElement(nfo_movie, "plot").text = self.outline
        ET.SubElement(nfo_movie, "runtime").text = self.length[:-2]
        ET.SubElement(nfo_movie, "director").text = self.director
        ET.SubElement(nfo_movie, "poster").text = self.poster[0]
        ET.SubElement(nfo_movie, "thumb").text = self.thumb[0]
        ET.SubElement(nfo_movie, "fanart").text = self.fanart[0]
        for actor in self.cast:
            nfo_actor = ET.SubElement(nfo_movie, "actor")
            ET.SubElement(nfo_actor, "name").text = actor
        ET.SubElement(nfo_movie, "maker").text = self.maker
        ET.SubElement(nfo_movie, "label").text = self.label
        for genre in self.genres:
            ET.SubElement(nfo_movie, "tag").text = genre
        for genre in self.genres:
            ET.SubElement(nfo_movie, "genre").text = genre
        ET.SubElement(nfo_movie, "num").text = self.designatio
        ET.SubElement(nfo_movie, "premiered").text = self.date
        ET.SubElement(nfo_movie, "cover").text = self.cover_url
        ET.SubElement(nfo_movie, "website").text = self.video_url

        nfo = ET.ElementTree(nfo_movie)

        for idx in range(self.slices):
            if not os.path.exists(dsts[idx]):
                nfo.write(dsts[idx], encoding="utf-8", xml_declaration=True)
        return True
