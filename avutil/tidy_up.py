#!/usr/bin/env python3
import sys
import argparse
import avutil

sys.setrecursionlimit(10000)


def get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Tidy up your personal video dir")
    parser.add_argument("-r", dest='recursive', action='store_true', help="search dir recursive")
    parser.add_argument("-i", "--in", dest='_in', help="video dir")
    parser.add_argument("-o", "--out", dest='_out', help="output dir")
    parser.add_argument("-p", "--proxy", dest='proxy',
                        help="http proxy address")
    return parser.parse_args(args)


def main():
    args = get_arguments()
    # args.dir
    if args._in == None:
        src_folder = './'
    else:
        src_folder = args._in

    # args.out
    if args._out == None:
        dst_folder = src_folder
    else:
        dst_folder = args._out

    # args.proxy
    if args.proxy == None:
        http_proxy = ""
    else:
        http_proxy = args.proxy

    # Search folder
    if args.recursive == True:
        videos = avutil.Search_folder(src_folder, recursive=True)
    else:
        videos = avutil.Search_folder(src_folder)

    for video in videos:
        try:
            # Pull AV info
            video.pull_info(http_proxy=http_proxy)
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
