import requests
import bs4


def encode(url):
    return "".join([chr((ord(rune) + 1) % 128) for rune in url])


class Bus:
    ''' Data source -- BUS
    '''
    base_url = encode("gsso9..vvv-i`uatr-bnl.")
    search_prefix = ""
    http_proxy = ""

    def __init__(self, http_proxy=""):
        self.http_proxy = http_proxy

    def Get(self, designatio):
        result = {}

        # URL for searching designatio
        URL = self.base_url + designatio

        # Using requests
        headers = {
            'Cache-Control': 'no-cache',
            'Accept': 'text/event-stream',
            'Accept-Encoding': 'gzip'
        }
        response = requests.get(URL, proxies={"http": self.http_proxy}, headers=headers)

        # parse html
        soup = bs4.BeautifulSoup(response.content, features="html.parser")

        # search title
        result["title"] = soup.select_one("body > .container > h3").string

        # cover image
        result["cover_url"] = soup.select_one(".bigImage")["href"]

        # infomation
        attributes = [e.string for e in soup.select(".header")]
        include = {
            "designatio":   '識別碼:' in attributes,
            "date":         '發行日期:' in attributes,
            "length":       '長度:' in attributes,
            "director":     '導演:' in attributes,
            "maker":        '製作商:' in attributes,
            "label":        '發行商:' in attributes,
            "series":       '系列:' in attributes,
            "genres":       '類別:' in attributes,
            "cast":         '演員' in attributes,
        }

        # Attributes Extract lambda function
        extract = {
            "designatio": lambda soup, i: i.select("span")[1].string,
            "date": lambda soup, i: str(i).split("</span> ")[1].rstrip("</p>"),
            "length": lambda soup, i: str(i).split("</span> ")[1].rstrip("</p>"),
            "director": lambda soup, i: i.a.string,
            "maker": lambda soup, i: i.a.string,
            "label": lambda soup, i: i.a.string,
            "series": lambda soup, i: i.a.string,
            "genres": lambda soup, i: [genre.string for genre in soup.select('a[href^="https://www.javbus.com/genre/"]')][2:],
            "cast": lambda soup, i: [actor.a.string for actor in soup.select('span[onmouseout^="hoverdiv"]')],
        }

        info = soup.select(".info > p")
        idx = 0

        for attr in ["designatio", "date", "length", "director", "maker", "label", "series", "genres", "cast"]:
            if include[attr]:
                result[attr] = extract[attr](soup, info[idx])
                idx += 1
        return result
