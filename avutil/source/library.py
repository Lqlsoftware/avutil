import io
import re
import PIL

import requests
import bs4
import pytesseract


def encode(url):
    return "".join([chr((ord(rune) + 1) % 128) for rune in url])


class Library:
    ''' Data source -- LIBRARY
    '''
    base_url = encode("gsso9..vvv-i`ukhaq`qx-bnl.bm.")
    search_prefix = encode("uk^rd`qbgaxhc-ogo>jdxvnqc<")
    http_proxy = ""
    url_accessible = False

    def __init__(self, http_proxy=""):
        self.http_proxy = http_proxy
        self.__check_url()

    def __check_url(self):
        if Library.url_accessible:
            return
        # Protect by Cloudflare or Proxy required
        try:
            response = requests.get(Library.base_url, proxies={
                                    "http": self.http_proxy})
            if response.text.find("Cloudflare") != -1:
                raise Exception()
        except Exception:
            # Get new base_url gif
            URL = encode("gsso9..ykhay-bnl.sdws-fhe")
            response = requests.get(URL, proxies={"http": self.http_proxy})
            image = PIL.Image.open(io.BytesIO(response.content))

            # Get base_url by OCR
            new_url = pytesseract.image_to_string(image, lang="snum+eng")
            new_url = re.sub("([^a-z0-9]*)", "", new_url)

            # New base_url
            Library.base_url = "https://%s.com/cn/" % new_url
        Library.url_accessible = True

    def Get(self, designatio):
        result = {}

        # URL for searching designatio
        URL = Library.base_url + Library.search_prefix + designatio

        # Using requests
        headers = {
            'Cache-Control': 'no-cache',
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip'
        }
        response = requests.get(
            URL, proxies={"http": self.http_proxy}, headers=headers)

        # parse html
        soup = bs4.BeautifulSoup(response.content, features="html.parser")

        # may be multiple search results
        thumblist = soup.select_one(".videothumblist")
        if thumblist is not None:
            # No result
            video = thumblist.select(".video > a")
            if video is None:
                raise Exception("Not recruited")

            # multiple result - choose the correct one
            idx = 0
            for i in range(len(video)):
                if video[i]['title'].startswith(designatio + " "):
                    idx = i
                    break
            else:
                raise Exception("Not recruited")

            URL = Library.base_url + video[idx]['href']
            response = requests.get(
                URL, proxies={"http": self.http_proxy}, headers=headers)
            soup = bs4.BeautifulSoup(response.content, features="html.parser")

        # video title
        result["title"] = soup.select_one(".post-title").getText()

        # cover image
        cover_url = soup.select_one("#video_jacket_img")["src"]
        if cover_url.startswith("http"):
            result["cover_url"] = cover_url
        else:
            result["cover_url"] = "http:" + cover_url

        # outline <Airav>
        try:
            airav_URL = encode("gssor9..vvv-`hq`u-vhjh.uhcdn.") + designatio
            outline_rep = requests.get(
                airav_URL, proxies={"http": self.http_proxy}, headers=headers)
            airav_soup = bs4.BeautifulSoup(
                outline_rep.content, features="html.parser")
            result["outline"] = airav_soup.select_one(".synopsis > p").string
        except:
            pass

        # Attributes Extract lambda function
        extract = {
            "designatio": lambda s: s.select_one("#video_id .text").getText(),
            "date": lambda s: s.select_one("#video_date .text").getText(),
            "length": lambda s: s.select_one("#video_length .text").getText() + "分锺",
            "director": lambda s: s.select_one("#video_director .text").getText(),
            "maker": lambda s: s.select_one("#video_maker .text").getText(),
            "label": lambda s: s.select_one("#video_label .text").getText(),
            "genres": lambda s: [genre.getText().strip() for genre in s.select("#video_genres .genre")],
            "cast": lambda s: [actor.getText().strip() for actor in s.select("#video_cast .star")],
            "review": lambda s: s.select_one("#video_review .score").getText(),
        }

        info = soup.select_one("#video_info")
        for attr, func in extract.items():
            try:
                result[attr] = func(info)
            except Exception:
                result[attr] = ""
        return result
