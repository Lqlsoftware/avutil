import os
import re
import requests
import xml.etree.ElementTree as ET

from avutil.bus import Bus
from avutil.library import Library


def strip(string):
    return re.sub(r"\/|\?|\*|\:|\||\\|\<|\>", "", string)


class Video:
    ''' Describe details of an video which includes:

        'designatio' 'title' 'cover_url' 'date' 'length'
        'director' 'maker' 'label' 'genres' 'cast'
    '''
    is_updated = False

    # File attributes
    file_dir  = ""
    file_name = ""
    file_path = ""
    file_type = ""

    # Video attributes
    designatio  = ""
    title       = ""
    subtitle    = False
    cover_url   = ""
    video_url   = ""
    date        = ""
    length      = ""
    director    = ""
    maker       = ""
    label       = ""
    review      = ""
    series      = []
    genres      = []
    cast        = []

    def __init__(self, designatio, file_path=""):
        self.designatio = designatio.upper()
        if file_path is not None:
            self.file_path = file_path
            self.file_dir  = os.path.dirname (file_path)
            self.file_name = os.path.basename(file_path)
            self.file_type = os.path.splitext(file_path)[1]
            self.subtitle  = os.path.splitext(file_path)[0].endswith("C")

    def __str__(self):
        if not self.is_updated:
            return "[文件 {0.file_path}]".format(self)
        else:
            return '''[文件 {0.file_path}]\n
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
    演员\t{0.cast}\n'''.format(self)

    def __gen_file_name(self):
        if len(self.title.encode()) > 251:
            if len(self.cast) == 1:
                overflow = 244 - len(self.title.encode()) - len(self.cast[0])
                return "{:}.. {:}".format(self.title[:overflow], self.cast[0])
            else:
                overflow = 245 - len(self.title.encode())
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
            print("Video not recruited or require proxy: ", self.file_path)
            return
        if self.subtitle:
            self.genres.append("中文字幕")
        self.is_updated = True

    def download_cover(self, dst_dir=None, http_proxy=""):
        ''' download cover of video title

            dst_dir will be orignal file_dir by default
        '''

        # Need pulling info
        if not self.is_updated:
            return False

        # User specify download dir
        if dst_dir is None:
            dst_dir = self.file_dir

        # Join path
        img_path = os.path.join(dst_dir, "{:}{:}".format(
            self.__gen_file_name(), ".jpg"))

        # Already exist or download dir not exist
        if not os.path.exists(dst_dir) or os.path.exists(img_path):
            return False

        # Proxy
        r = requests.get(self.cover_url, stream=True, proxies={"http": http_proxy})

        # Download
        if r.status_code == 200:
            with open(img_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
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
            dst_dir = self.file_dir

        # Join path
        dst_path = os.path.join(dst_dir, "{:}{:}".format(
            self.__gen_file_name(), self.file_type))

        # Already exist or rename dir not exist
        if not os.path.exists(dst_dir) or os.path.exists(dst_path):
            return False

        # Rename
        os.rename(self.file_path, dst_path)
        self.file_path = dst_path
        self.file_dir = os.path.dirname(dst_path)
        self.file_name = os.path.basename(dst_path)
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
            dst_dir = self.file_dir

        # Join path
        dst_path = os.path.join(dst_dir, "{:}{:}".format(self.__gen_file_name(), ".nfo"))

        # Already exist or dst dir not exist
        if not os.path.exists(dst_dir) or os.path.exists(dst_path):
            return False

        nfo_movie = ET.Element("movie")
        ET.SubElement(nfo_movie, "title").text = self.title
        ET.SubElement(nfo_movie, "set")
        ET.SubElement(nfo_movie, "studio").text = self.maker
        ET.SubElement(nfo_movie, "year").text = self.date[:4]
        ET.SubElement(nfo_movie, "outline").text = self.title
        ET.SubElement(nfo_movie, "plot").text = self.title
        ET.SubElement(nfo_movie, "runtime").text = self.length[:-2]
        ET.SubElement(nfo_movie, "director").text = self.director
        ET.SubElement(nfo_movie, "poster").text = self.__gen_file_name() + ".jpg"
        ET.SubElement(nfo_movie, "thumb").text = self.__gen_file_name() + ".jpg"
        ET.SubElement(nfo_movie, "fanart").text = self.__gen_file_name() + ".jpg"
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
        nfo.write(dst_path, encoding="utf-8", xml_declaration=True)
