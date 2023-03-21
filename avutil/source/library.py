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
    base_url = encode("gssor9..vvv-i`ukhaq`qx-bnl.bm.")
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
            URL = encode("gssor9..ykhay-bnl.sdws-fhe")
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
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': 'https://www.javlibrary.com',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
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
            matched = [i for i in range(0, len(video)) if video[i]['title'].startswith(designatio + " ") ]
            idx = None
            if len(matched) == 0:
                raise Exception("Not recruited")
            elif len(matched) == 1:
                idx = matched[0]
            else:
                if len(matched) == 2:
                    idx0 = matched[0]
                    idx1 = matched[1]
                    title0 = video[idx0]['title']
                    title1 = video[idx1]['title']
                    if title1.startswith(title0):
                        idx = matched[idx0]
                    elif title0.startswith(title1):
                        idx = matched[idx1]
                if idx is None:
                    print("Multiple Choice:")
                    for i in range(0, len(matched)):
                        print("  [%d] %s" % (i, video[matched[i]]['title']))
                    idx = matched[int(input("\nSelect > "))]

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
            "length": lambda s: s.select_one("#video_length .text").getText(),
            "director": lambda s: s.select_one("#video_director .text").getText(),
            "maker": lambda s: s.select_one("#video_maker .text").getText(),
            "label": lambda s: s.select_one("#video_label .text").getText(),
            "genres": lambda s: [genre.getText().strip() for genre in s.select("#video_genres .genre")],
            "cast": lambda s: [actor.getText().strip() for actor in s.select("#video_cast .star")],
            "review": lambda s: s.select_one("#video_review .score").getText().lstrip("(").rstrip(")"),
        }

        info = soup.select_one("#video_info")
        for attr, func in extract.items():
            try:
                result[attr] = func(info)
            except Exception:
                result[attr] = ""
        return result
