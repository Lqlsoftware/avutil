import requests
import bs4


def encode(url):
    return "".join([chr((ord(rune) + 1) % 128) for rune in url])


class Library:
    ''' Data source -- LIBRARY
    '''
    base_url = ""

    def __init__(self):
        self.base_url = encode(
            "gsso9..vvv-i`ukhaq`qx-bnl.bm.uk^rd`qbgaxhc-ogo>jdxvnqc<")

    def Get(self, designatio, use_proxy=False, http_proxy=None):
        result = {}

        # URL for searching designatio
        URL = self.base_url + designatio

        # Using requests
        headers = {
            'Cache-Control': 'no-cache',
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip'
        }
        if use_proxy:
            response = requests.get(
                URL, proxies={"http": http_proxy}, headers=headers)
        else:
            response = requests.get(URL, headers=headers)

        # parse html
        response.iter_lines()
        soup = bs4.BeautifulSoup(response.content, features="html.parser")

        # search title
        result["title"] = soup.select_one(".post-title").getText()

        # cover image
        result["cover_url"] = "http:" + \
            soup.select_one("#video_jacket_img")["src"]

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
            result[attr] = func(info)
        return result
