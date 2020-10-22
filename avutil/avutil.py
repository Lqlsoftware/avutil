import os
import re
import requests

from bs4 import BeautifulSoup

class Video:
    ''' Describe details of an video which includes:

        'designatio' 'title' 'cover_url' 'publish_date' 'video_length'
        'director' 'manufacturer' 'publisher' 'genres' 'actors'
    '''
    file_dir        = ""
    file_name       = ""
    file_path       = ""
    file_type       = ""
    designatio      = ""
    title           = ""
    cover_url       = ""
    publish_date    = ""
    video_length    = ""
    director        = ""
    manufacturer    = ""
    publisher       = ""
    series          = []
    genres          = []
    actors          = []

    def __init__(self, designatio, file_path=""):
        self.designatio = designatio
        if file_path is not None:
            self.file_path = file_path
            self.file_dir = os.path.dirname(file_path)
            self.file_name = os.path.basename(file_path)
            self.file_type = os.path.splitext(file_path)[1]

    def __str__(self):
        return '''[文件 {0.file_path}]\n
    标题\t{0.title}
    番号\t{0.designatio}
    发行日期\t{0.publish_date}
    影片长度\t{0.video_length}
    导演\t{0.director}
    制作商\t{0.manufacturer}
    发行商\t{0.publisher}
    系列\t{0.series}
    类别\t{0.genres}
    演员\t{0.actors}\n'''.format(self)

    def pull_info(self, use_proxy=False, http_proxy="http://127.0.0.1:1087"):
        ''' Pull video details by designatio from JAVBUS (currently). 

            use_proxy is set to False by default

            http_proxy is set to http://127.0.0.1:1087 by default
        '''

        # URL of JAVBUS searching designatio
        URL = "http://www.javbus.com/" + self.designatio
        try:
            # request library
            if use_proxy:
                response = requests.get(URL, proxies={"http": http_proxy})
            else:
                response = requests.get(URL)

            # parse html
            soup = BeautifulSoup(response.content, features="html.parser")

            # search title
            self.title = soup.select_one("body > .container > h3").string

            # cover image
            self.cover_url = soup.select_one(".bigImage")["href"]

            # infomation
            attributes = [e.string for e in soup.select(".header")]
            include = {
                "designatio": '識別碼:' in attributes,
                "publish_date": '發行日期:' in attributes,
                "video_length": '長度:' in attributes,
                "director": '導演:' in attributes,
                "manufacturer": '製作商:' in attributes,
                "publisher": '發行商:' in attributes,
                "series": '系列:' in attributes,
                "genres": '類別:' in attributes,
                "actors": '演員' in attributes,
            }

            extract = {
                "designatio": lambda soup, i: i.select("span")[1].string,
                "publish_date": lambda soup, i: str(i).split("</span> ")[1].rstrip("</p>"),
                "video_length": lambda soup, i: str(i).split("</span> ")[1].rstrip("</p>"),
                "director": lambda soup, i: i.a.string,
                "manufacturer": lambda soup, i: i.a.string,
                "publisher": lambda soup, i: i.a.string,
                "series": lambda soup, i: i.a.string,
                "genres": lambda soup, i: [genre.string for genre in soup.select('a[href^="https://www.javbus.com/genre/"]')][2:],
                "actors": lambda soup, i: [actor.a.string for actor in soup.select('span[onmouseout^="hoverdiv"]')],
            }
            info = soup.select(".info > p")
            idx = 0

            for attr in ["designatio", "publish_date", "video_length", "director", "manufacturer", "publisher", "series", "genres", "actors"]:
                if include[attr]:
                    self.__setattr__(attr, extract[attr](soup, info[idx]))
                    idx += 1

        except Exception as e:
            raise Exception("Video Not Found or Require proxy", e)

    def download_cover(self, dst_dir=None, use_proxy=False, http_proxy="http://127.0.0.1:1087"):
        ''' download cover of video title

            dst_dir will be orignal file_dir by default
        '''
        if dst_dir is None:
            dst_dir = self.file_dir
        # Join path
        img_path = os.path.join(dst_dir, self.title + '.jpg')
        if not os.path.exists(dst_dir) or os.path.exists(img_path):
            return False
        # Proxy
        if use_proxy:
            r = requests.get(self.cover_url, stream=True, proxies={"http": http_proxy})
        else:
            r = requests.get(self.cover_url, stream=True)
        # Download
        if r.status_code == 200:
            with open(img_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

    def rename(self, dst_dir=None):
        ''' rename video files by title

            dst_dir will be orignal file_dir by default
        '''
        if dst_dir is None:
            dst_dir = self.file_dir
        # Join path
        dst_path = os.path.join(dst_dir, self.title + self.file_type)
        if not os.path.exists(dst_dir) or os.path.exists(dst_path):
            return False
        os.rename(self.file_path, dst_path)
        return True


def Extract_designatio(name):
    ''' Extract designatio from given name (string)
    '''
    match = re.match(r"([a-zA-Z]+[\-\_][0-9]+)", name)
    if match is None:
        return None
    return match.groups()[0]


def Search_folder(folder, media_suffix={"mp4", "wmv", "avi", "mkv"}):
    ''' Search specify media type of video recursively in folder
    '''
    videos = []
    # walk folder
    list_dirs = os.walk(folder)
    for folder, dirs, files in list_dirs:
        for f in files:
            file_name = f.split('.')
            # exclude other type of file
            if len(file_name) <= 1 or file_name[-1] not in media_suffix:
                continue
            # extract
            designatio = Extract_designatio(f)
            if designatio is None:
                continue
            # append in list
            videos.append(Video(designatio=designatio, file_path=os.path.join(folder, f)))
    return videos