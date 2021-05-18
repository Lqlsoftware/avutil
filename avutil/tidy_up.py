#!/usr/bin/env python3
import sys
import argparse
import avutil

sys.setrecursionlimit(10000)


def get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Tidy up your personal video dir")
    parser.add_argument("-r", dest='recursive', action='store_true',
        help="search dir recursively")
    parser.add_argument("-i", "--in", dest='IN',
        help="video input dir")
    parser.add_argument("-o", "--out", dest='OUT',
        help="video output dir")
    parser.add_argument("-p", "--proxy", dest='proxy',
        help="http proxy address")
    parser.add_argument("-s", "--source", dest='source',
        help="data source of video info, 'library' or 'bus'")
    return parser.parse_args(args)


def main():
    args = get_arguments()
    # args.dir
    if args.IN is None:
        src_folder = './'
    else:
        src_folder = args.IN

    # args.out
    if args.OUT is None:
        dst_folder = src_folder
    else:
        dst_folder = args.OUT

    # args.proxy
    if args.proxy is None:
        http_proxy = ""
    else:
        http_proxy = args.proxy

    # Search folder
    if args.recursive == True:
        videos = avutil.Search_folder(src_folder, recursive=True)
    else:
        videos = avutil.Search_folder(src_folder)

    # Data source
    if args.source == "bus":
        source = avutil.Bus
    else:
        source = avutil.Library

    for designatio, file_paths in videos.items():
        try:
            video = avutil.Video(designatio, file_paths)

            # Pull AV info
            video.pull_info(source=source, http_proxy=http_proxy)
            print(video)

            # Download cover
            video.download_cover(dst_dir=dst_folder, http_proxy=http_proxy)

            # Tidy up
            video.rename(dst_dir=dst_folder)

            # Save video info as .nfo
            video.save_info(dst_dir=dst_folder)
        except Exception as e:
            print("WARN:", e)
            pass
