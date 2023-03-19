import requests
import bs4


def encode(url):
    return "".join([chr((ord(rune) + 1) % 128) for rune in url])


class Bus:
    ''' Data source -- BUS
    '''
    base_url = encode("gssor9..vvv-i`uatr-bnl.")
    search_prefix = encode("rd`qbg.")
    http_proxy = ""

    def __init__(self, http_proxy=""):
        self.http_proxy = http_proxy

    def Get(self, designatio):
        result = {}

        # URL for searching designatio
        URL = self.base_url + self.search_prefix + designatio

        # Using requests
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'cookie': 'existmag=all',
            'referer': 'https://www.javbus.com',
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

        search_result = soup.select(".item")
        if search_result is None or len(search_result) == 0:
            # No result
            raise Exception("Not recruited")

        # multiple result - choose the correct one
        matched = []
        for r in search_result:
            id = r.find("date").string
            if id == designatio:
                title = r.find("img").attrs["title"]
                matched.append((id + " " + title, r.find("a").attrs["href"]))

        idx = 0
        if len(matched) > 1:
            print("Multiple Choice:")
            for i in range(0, len(matched)):
                print("  [%d] %s" % (i, matched[i][0]))
            idx = int(input("\nSelect > "))
        URL = matched[idx][1]

        # get info
        response = requests.get(
            URL, proxies={"http": self.http_proxy}, headers=headers)
        soup = bs4.BeautifulSoup(response.content, features="html.parser")

        # search title
        result["title"] = soup.select_one("body > .container > h3").string

        # cover image
        cover_url = soup.select_one(".bigImage")["href"]
        if cover_url.startswith('/'):
            cover_url = self.base_url + cover_url
        result["cover_url"] = cover_url

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
            "length": lambda soup, i: str(i).split("</span> ")[1].rstrip("</p>").strip().rstrip("分鐘"),
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
