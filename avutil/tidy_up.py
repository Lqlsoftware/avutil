#!/usr/bin/env python3
import sys
import argparse
import threading
import avutil

from multiprocessing.dummy import Pool

sys.setrecursionlimit(10000)

src_folder = "./"
dst_folder = "./"
http_proxy = ""
source = avutil.Library
thread = 8
with_poster = False


def VideoProcess(video):
    global src_folder
    global dst_folder
    global http_proxy
    global source
    global thread
    global with_poster

    try:
        designatio, file_paths = video
        video = avutil.Video(designatio, file_paths)

        # Pull AV info
        video.pull_info(source=source, http_proxy=http_proxy)
        if video.is_updated:
            print("[%8s] %s" % (video.designatio, video.title))

        # Download cover
        video.download_cover(dst_dir=dst_folder,
                             http_proxy=http_proxy, with_poster=with_poster)

        # Tidy up
        video.rename(dst_dir=dst_folder)

        # Save video info as .nfo
        video.save_info(dst_dir=dst_folder)
    except Exception as e:
        print("WARN:", e)
        pass


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
    parser.add_argument("-t", "--thread", dest='thread', type=int,
                        help="threads num, use multi-threads to download info & images")
    parser.add_argument("--with-poster", dest='with_poster', action='store_true',
                        help="save poster")
    return parser.parse_args(args)


def main():

    global src_folder
    global dst_folder
    global http_proxy
    global source
    global thread
    global with_poster

    args = get_arguments()
    # args.dir
    if args.IN is not None:
        src_folder = args.IN

    # args.out
    if args.OUT is not None:
        dst_folder = args.OUT

    # args.proxy
    if args.proxy is not None:
        http_proxy = args.proxy

    # Data source
    if args.source == "bus":
        source = avutil.Bus

    # Gen poster
    if args.with_poster == True:
        with_poster = True

    # Threads num
    if args.thread is not None:
        thread = int(args.thread)
    else:
        thread = 4

    # Search folder
    if args.recursive == True:
        videos = avutil.Search_folder(src_folder, recursive=True)
    else:
        videos = avutil.Search_folder(src_folder)

    # Threads work
    jobs = [v for v in videos.items()]
    pool = Pool(thread)
    pool.map(VideoProcess, jobs)
    pool.close()
    pool.join()