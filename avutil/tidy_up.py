#!/usr/bin/env python3
import sys
import argparse
import pickle
import avutil

sys.setrecursionlimit(10000)


def get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Tidy up your personal video dir")
    parser.add_argument("-d", "--dir", dest='dir', help="video dir")
    parser.add_argument("-o", "--out", dest='out', help="output dir")
    parser.add_argument("-s", "--save", dest='save',
                        help="save video info pkl")
    parser.add_argument("-p", "--proxy", dest='proxy',
                        help="http proxy address")
    return parser.parse_args(args)


def main():
    args = get_arguments()
    # args.dir
    if args.dir == None:
        src_folder = './'
    else:
        src_folder = args.dir

    # args.out
    if args.out == None:
        dst_folder = src_folder
    else:
        dst_folder = args.out

    # args.save
    if args.save == None:
        pkl_save = None
    else:
        pkl_save = args.save

    # args.proxy
    if args.proxy == None:
        use_proxy = False
        http_proxy = ""
    else:
        use_proxy = True
        http_proxy = args.proxy

    # Search folder
    videos = avutil.Search_folder(src_folder)

    for video in videos:
        try:
            # Pull AV info
            video.pull_info(use_proxy=use_proxy, http_proxy=http_proxy)
            print(video)

            # Download cover
            video.download_cover(dst_dir=dst_folder,
                                 use_proxy=use_proxy, http_proxy=http_proxy)

            # Tidy up
            video.rename(dst_dir=dst_folder)
        except Exception:
            pass

    # Save video info pkl
    if pkl_save is not None:
        with open(pkl_save, 'wb') as f:
            pickle.dump(videos, f)
