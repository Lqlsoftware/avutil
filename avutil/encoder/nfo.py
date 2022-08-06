import xml.etree.ElementTree as ET


class NFOEncoder:

    ext = ".nfo"

    def __init__(self):
        pass

    def encode(self, video: dict):
        ''' encode video info as nfo format (XML)

            return bytes that encode using nfo format 

            NFO is appliable in Jellyfin / Emby.
        '''

        nfo_movie = ET.Element("movie")
        ET.SubElement(nfo_movie, "title").text = video.get("title")
        ET.SubElement(nfo_movie, "set")
        ET.SubElement(nfo_movie, "studio").text = video.get("maker")
        ET.SubElement(nfo_movie, "year").text = video.get("date")[:4]
        ET.SubElement(nfo_movie, "outline").text = video.get("outline")
        ET.SubElement(nfo_movie, "plot").text = video.get("outline")
        ET.SubElement(nfo_movie, "runtime").text = video.get("length")[:-2]
        ET.SubElement(nfo_movie, "director").text = video.get("director")
        ET.SubElement(nfo_movie, "poster").text = video.get("poster_path")
        ET.SubElement(nfo_movie, "thumb").text = video.get("thumb_path")
        ET.SubElement(nfo_movie, "fanart").text = video.get("fanart_path")
        for actor in video.get("cast"):
            nfo_actor = ET.SubElement(nfo_movie, "actor")
            ET.SubElement(nfo_actor, "name").text = actor
        ET.SubElement(nfo_movie, "maker").text = video.get("maker")
        ET.SubElement(nfo_movie, "label").text = video.get("label")
        for serie in video.get("series"):
            ET.SubElement(nfo_movie, "tag").text = serie
        for genre in video.get("genres"):
            ET.SubElement(nfo_movie, "genre").text = genre
        ET.SubElement(nfo_movie, "num").text = video.get("designatio")
        ET.SubElement(nfo_movie, "premiered").text = video.get("date")
        ET.SubElement(nfo_movie, "cover").text = video.get("cover_url")
        ET.SubElement(nfo_movie, "website").text = video.get("video_url")

        nfo = ET.ElementTree(nfo_movie).getroot()

        return ET.tostring(nfo, encoding='utf8', method='xml')
