#!/usr/bin/env python3
import sys
import argparse
import avutil

def get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Tidy up your personal video dir")
    parser.add_argument("-d", "--dir", dest='dir', help="video dir")
    parser.add_argument("-o", "--out", dest='out', help="output dir")
    parser.add_argument("-p", "--proxy", dest='proxy', help="http proxy address")
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

    # args.proxy
    if args.proxy == None:
        use_proxy = False
        http_proxy = ""
    else:
        use_proxy = True
        http_proxy = args.proxy

    # Search folder
    avs = avutil.Search_folder(src_folder)

    for av in avs:
        try:
            # Pull AV info 
            av.pull_info(use_proxy=use_proxy, http_proxy=http_proxy)
            print(av)

            # Download cover
            av.download_cover(dst_dir=dst_folder, use_proxy=use_proxy, http_proxy=http_proxy)

            # Tidy up
            av.rename(dst_dir=dst_folder)
        except Exception:
            pass