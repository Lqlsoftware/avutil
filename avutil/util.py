import os
import re

from avutil.video import Video

def Extract_designatio(name):
    ''' Extract designatio from given name (string)
    '''
    # Remove video type
    names = name.split('.')
    if len(name) < 1:
        name = names[0]
    else:
        name = ".".join(names[:-1])

    # Re match
    match = re.match(r".*?([a-zA-Z]+[\-\_\s]*?[0-9]+)", name)
    if match is None:
        return None
    return match.groups()[0]


def Search_folder(folder, media_suffix={"mp4", "wmv", "avi", "mkv"}, recursive=False):
    ''' Search specify media type of video recursively in folder
    '''

    videos = []
    list_dirs = []
    if recursive:
        # walk folder
        list_dirs = os.walk(folder)
    else:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        list_dirs = [(folder, None, files)]

    for folder, _, files in list_dirs:
        for f in files:
            file_name = f.split('.')

            # exclude other type of file
            if len(file_name) <= 1 or file_name[-1].lower() not in media_suffix:
                continue

            # info already saved
            if os.path.exists(os.path.join(folder, ".".join(file_name[:-1]) + ".nfo")):
                continue

            # extract
            designatio = Extract_designatio(f)
            if designatio is None:
                continue

            # append in list
            v = Video(designatio=designatio, file_path=os.path.join(folder, f))
            videos.append(v)
    return videos
