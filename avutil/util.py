import os
import re

from avutil.video import Video

def Extract_designatio(file_name):
    ''' Extract designatio from given name (string)
    '''
    # Remove video type
    file_name = os.path.splitext(file_name)[0]

    # Re match
    match = re.match(r".*?([a-zA-Z]+[\-\_\s]*?[0-9]+)", file_name)
    if match is None:
        return None
    return match.groups()[0]


def Search_folder(folder, media_suffix={".mp4", ".wmv", ".avi", ".mkv"}, recursive=False):
    ''' Search specify media type of video recursively in folder

        return map{ designatio -> [file_path] }
    '''

    videos = {}
    list_dirs = []
    if recursive:
        # walk folder
        list_dirs = os.walk(folder)
    else:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        list_dirs = [(folder, None, files)]

    for folder, _, files in list_dirs:
        for f in files:
            file_name = os.path.splitext(f)

            # exclude other type of file
            if file_name[1].lower() not in media_suffix:
                continue

            # info already saved
            if os.path.exists(os.path.join(folder, file_name[0] + ".nfo")):
                continue

            # extract
            designatio = Extract_designatio(f)
            if designatio is None:
                continue

            if designatio not in videos:
                videos[designatio] = []
            videos[designatio].append(os.path.join(folder, f))
    return videos
