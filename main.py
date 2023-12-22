# This program can take a url in the form www.example.com/photo/pic[0-9].jpg
# and expand it to 10 different urls or it will read a file containing a list
# of urls then it will download the data at those urls into a numerically
# sequential folder.
# Notes:
#   Only one set of [] are possible in this version, and there is no error
#     checking to make sure there is a matching bracket.
#   Ranges can only be numbers, no letters in this version.
#   A range from [0-10] translates to 00, 01, 02, etc.

import argparse
import logging
import pathlib
import urllib.parse
import os

from download_manager import DownloadManager, DownloadItem


from fusker.input_generator import generate_input_from_url


user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36"


class Args:
    pad: str = None
    dest: pathlib.Path = None
    threads: int = None
    quiet: bool = None
    debug: bool = None
    referrer: str = None
    url: str = None
    file: pathlib.Path


def find_next_dir(base_dir: pathlib.Path) -> pathlib.Path:
    d = 0
    next_dir = base_dir / str(d)
    while next_dir.exists():
        d += 1
        next_dir = base_dir / str(d)
    return


def get_referer(args: Args, url: str):
    if args.referrer:
        return args.referrer
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def main(args: Args):
    dest = find_next_dir(args.dest)
    logging.info(f"Downloading files to {dest}")
    manager = DownloadManager(
        output_directory=dest,
        thread_count=args.threads,
        use_content_disposition_header_for_filename=True,
    )

    if args.url is not None:
        urls = generate_input_from_url(args.url, args.pad)
    else:
        urls = []
        with args.file.open('r') as f:
            for line in f:
                urls.append(line.strip())

    logging.info(f"Downloading {len(urls)} items")
    for url in urls:
        manager.add_item_to_queue(DownloadItem(
            url,
            additional_headers={
                'Referer': get_referer(args, url),
                'User-Agent': user_agent,
            }
        ))

    manager.start()
    manager.wait_for_downloads_to_finish()
    if manager.failed_files:
        with open(args.dest / 'failed.txt') as f:
            for failed in manager.failed_files:
                logging.error(failed)
                f.write(f'{failed.url}{os.linesep}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Takes a url of the form "
                      "www.example.com/photos/pic[0-9].jpg and expands it.")
    parser.add_argument("-p", "--pad", default="", type=lambda x: x[0:1],
                        help="Single character to pad "
                        "short expansions with. [0-10] becomes 00, 01, etc. "
                        "with a padding of \"0\". Defaults to no padding.")
    parser.add_argument("-d", "--dest", type=pathlib.Path,
                        default=pathlib.Path('.'),
                        help="Destination to place the folder containing the "
                             "files.")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="Number of threads.")
    log_level_group = parser.add_mutually_exclusive_group(required=False)
    
    parser.add_argument("-r", "--referrer")
    log_level_group.add_argument("-q", "--quiet", action="store_true")
    log_level_group.add_argument("--debug", action="store_true")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="URL to expand")
    group.add_argument("-f", "--file", type=pathlib.Path,
                       help="File containing a list of URLs to download.")
    
    args: Args = parser.parse_args()

    log_level = logging.INFO
    if args.quiet:
        log_level = logging.WARNING
    elif args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)
    main(args)