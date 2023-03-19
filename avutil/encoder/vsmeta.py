import base64
import hashlib
import time
import bitstring


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


class VSMETAEncoder:

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
        bs.append(b"\x08\x01")

        # Main Title
        bs.append(b"\x12")
        bs.append(str2bytes(video.get("designatio")))
        bs.append(b"\x1a")
        bs.append(str2bytes(video.get("designatio")))

        # Title
        bs.append(b"\x22")
        bs.append(str2bytes(video.get("title")))

        # Date
        bs.append(b"\x28\xe6\x0f\x32")
        bs.append(str2bytes(video.get("date")))

        # Locked (not update from internet)
        bs.append(b"\x38\x01")

        # Summary
        if (len(video.get("outline")) > 0):
            bs.append(b"\x42")
            bs.append(str2bytes(video.get("outline")))

        # Meta json (null)
        bs.append(b"\x4a\x04\x6e\x75\x6c\x6c")

        # Group Info
        info = bitstring.BitStream()
        # Cast
        for actor in video.get("cast"):
            info.append(b"\x0a")
            info.append(str2bytes(actor))
        # Director
        info.append(b"\x12")
        info.append(str2bytes(video.get("director")))
        # Genre
        for genre in video.get("genres"):
            info.append(b"\x1a")
            info.append(str2bytes(genre))
        # End of Group
        bs.append(b"\x52")
        bs.append(int2bytes(len(info)))
        bs.append(info)

        # Classification
        bs.append(b"\x5a")
        bs.append(str2bytes("R18+"))

        # Poster (BASE64 + MD5)
        bs.append(b"\x8a\x01")
        poster_b64_bytes = base64.b64encode(video.get('poster'))
        bs.append(int2bytes(len(poster_b64_bytes)))
        bs.append(poster_b64_bytes)
        bs.append(b"\x92\x01")
        bs.append(str2bytes(hashlib.md5(poster_b64_bytes).hexdigest()))

        # Group Info
        info = bitstring.BitStream()
        # Background (BASE64 + MD5)
        info.append(b"\x0a")
        background_b64_bytes = base64.b64encode(video.get('fanart'))
        info.append(int2bytes(len(background_b64_bytes)))
        info.append(background_b64_bytes)
        info.append(b"\x12")
        info.append(str2bytes(hashlib.md5(background_b64_bytes).hexdigest()))
        # Timestamp
        info.append(b"\x18")
        info.append(int2bytes(int(time.time() // 1000)))
        # End of Group
        bs.append(b"\xaa\x01")
        bs.append(int2bytes(len(info)))
        bs.append(info)

        return bs.bytes
