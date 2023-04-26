import base64
import hashlib
import time
import bitstring


def trim(string: str, limit: int):
    ''' Trim string to fit upperlimit

    '''
    ret = string
    while len(ret.encode("utf-8")) > limit:
        ret = ret[:-1]
    return ret


def int2bytes(integer: int):
    ''' Encode integer as bytes with vsmeta format

        eg: 128 => b'0x8001'
            127 => b'0x7f'
    '''
    bs = bitstring.BitStream()
    while integer >= 128:
        # Mark highest digit of uint8 with 0x80
        bs.append(((integer % 128) | 0x80).to_bytes(1, 'little'))
        integer = integer >> 7
    bs.append(integer.to_bytes(1, 'little'))
    return bs.bytes


def str2bytes(string: str):
    ''' Encode string as bytes with vsmeta format

        bytes: [toBytes(len), string]
    '''
    bs = bitstring.BitStream()
    bs.append(int2bytes(len(string.encode("utf-8"))))
    bs.append(string.encode("utf-8"))
    return bs.bytes


def img2bytes(image: bytes):
    ''' Encode image as bytes with vsmeta format

        bytes: str2bytes(base64 + \\n every 76 chars)
    '''
    b64_bytes = base64.b64encode(image)

    out_str = ''
    count = 0
    for chr in b64_bytes.decode():
        if count == 76:
            count = 0
            out_str += '\n'
        out_str += chr
        count += 1
    bs = bitstring.BitStream()
    bs.append(str2bytes(out_str))
    return bs.bytes

class VSMETAEncoder:

    TAG_FILE_HEADER_MOVIE = b'\x08\x01'

    TAG_SHOW_TITLE = b'\x12'
    TAG_SHOW_TITLE2 = b'\x1A'
    TAG_EPISODE_TITLE = b'\x22'
    TAG_YEAR = b'\x28'
    TAG_EPISODE_RELEASE_DATE = b'\x32'
    TAG_EPISODE_LOCKED = b'\x38'
    TAG_CHAPTER_SUMMARY = b'\x42'
    TAG_EPISODE_META_JSON = b'\x4A'
    TAG_GROUP1 = b'\x52'
    TAG_CLASSIFICATION = b'\x5A'
    TAG_RATING = b'\x60'
    TAG_EPISODE_THUMB_DATA = b'\x8a'
    TAG_EPISODE_THUMB_MD5 = b'\x92'
    TAG_GROUP2 = b'\xAA'

    TAG1_CAST = b'\x0A'
    TAG1_DIRECTOR = b'\x12'
    TAG1_GENRE = b'\x1A'
    TAG1_WRITER = b'\x22'

    TAG2_BACKDROP_DATA = b'\x0a'
    TAG2_BACKDROP_MD5 = b'\x12'
    TAG2_TIMESTAMP = b'\x18'

    ext = ".vsmeta"

    def __init__(self):
        pass

    def encode(self, video: dict):
        ''' encode video info as vsmeta format

            return bytes that encode using vsmeta format 

            VSMETA is appliable in Synology Video Station
        '''
        bs = bitstring.BitStream()

        # Header
        bs.append(self.TAG_FILE_HEADER_MOVIE)

        # Main Title
        bs.append(self.TAG_SHOW_TITLE)
        bs.append(str2bytes(trim(video.get("designatio"), 255)))
        bs.append(self.TAG_SHOW_TITLE2)
        bs.append(str2bytes(trim(video.get("title"), 255)))

        # Title
        bs.append(self.TAG_EPISODE_TITLE)
        bs.append(str2bytes(trim(video.get("title"), 255)))

        # Date
        bs.append(self.TAG_YEAR)
        if len(video.get("date")) > 4:
            bs.append(int2bytes(int(video.get("date")[:4])))
            bs.append(self.TAG_EPISODE_RELEASE_DATE)
            bs.append(str2bytes(video.get("date")))
        else:
            bs.append(int2bytes(0))

        # Locked (not update from internet)
        bs.append(self.TAG_EPISODE_LOCKED)
        bs.append(b"\x01")

        # Summary
        if (len(video.get("outline")) > 0):
            bs.append(self.TAG_CHAPTER_SUMMARY)
            bs.append(str2bytes(video.get("outline")))

        # Meta json (null)
        bs.append(self.TAG_EPISODE_META_JSON)
        bs.append(str2bytes("null"))

        # Group Info
        info = bitstring.BitStream()
        # Cast
        for actor in video.get("cast"):
            info.append(self.TAG1_CAST)
            info.append(str2bytes(actor))
        # Director
        info.append(self.TAG1_DIRECTOR)
        info.append(str2bytes(video.get("director")))
        # Genre
        for genre in video.get("genres"):
            info.append(self.TAG1_GENRE)
            info.append(str2bytes(genre))
        info.append(self.TAG1_WRITER)
        info.append(str2bytes(video.get("maker")))
        # End of Group
        bs.append(self.TAG_GROUP1)
        bs.append(int2bytes(len(info.bytes)))
        bs.append(info)

        # Classification
        if len(video.get("mpaa")) > 0:
            bs.append(self.TAG_CLASSIFICATION)
            bs.append(str2bytes(video.get("mpaa")))

        # Rating
        if len(video.get("review")) > 0:
            bs.append(self.TAG_RATING)
            bs.append(int2bytes(int(float(video.get("review")) * 10)))

        # Poster (BASE64 + MD5)
        if len(video.get('poster')) > 0:
            bs.append(self.TAG_EPISODE_THUMB_DATA)
            bs.append(b"\x01")
            bs.append(img2bytes(video.get('poster')))
            bs.append(self.TAG_EPISODE_THUMB_MD5)
            bs.append(b"\x01")
            bs.append(str2bytes(hashlib.md5(video.get('poster')).hexdigest()))

        # Group Info
        info = bitstring.BitStream()
        # Background (BASE64 + MD5)
        if len(video.get('fanart')) > 0:
            info.append(self.TAG2_BACKDROP_DATA)
            info.append(img2bytes(video.get('fanart')))
            info.append(self.TAG2_BACKDROP_MD5)
            info.append(str2bytes(hashlib.md5(video.get('fanart')).hexdigest()))
        info.append(self.TAG2_TIMESTAMP)
        info.append(int2bytes(int(time.time() // 1000)))
        # End of Group
        bs.append(self.TAG_GROUP2)
        bs.append(b'\x01')
        bs.append(int2bytes(len(info.bytes)))
        bs.append(info)

        return bs.bytes
