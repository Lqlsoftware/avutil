#!/usr/bin/env python3
import sys
import argparse
import avutil

def get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Tidy up your personal video dir")
    parser.add_argument("-d", "--dir", dest='dir', help="video dir")
    parser.add_argument("-p", "--proxy", dest='proxy', help="http proxy address")
    return parser.parse_args(args)


def main():
    args = get_arguments()
    # args.file
    if args.dir == None:
        folder = './'
    else:
        folder = args.dir

    # args.proxy
    if args.proxy == None:
        use_proxy = False
        http_proxy = ""
    else:
        use_proxy = True
        http_proxy = args.proxy
    # Search folder
    avs = avutil.Search_folder(folder)

    for av in avs:
        # Pull AV info 
        av.pull_info(use_proxy=use_proxy, http_proxy=http_proxy)
        print(av)

        # Download cover
        av.download_cover(use_proxy=use_proxy, http_proxy=http_proxy)

        # Tidy up
        av.rename()