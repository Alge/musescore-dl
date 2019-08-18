#!/usr/bin/env python3

import argparse
import tempfile
from downloader import Downloader
from shutil import move
from sys import exit

parser = argparse.ArgumentParser()

parser.add_argument('url', help='Url to a musescore.com score page. Ex: https://musescore.com/user/918006/scores/1439901')
parser.add_argument('--midi', action='store_true', help='Download PDF file')
parser.add_argument('--pdf', action='store_true', help='Download midi file')
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.0')
parser.add_argument('-o', help='output file name without extension', default=None)

args = parser.parse_args()

d = Downloader(args.url)

filename = d.score_id
if args.o:
    filename = args.o

if args.pdf:
    tmp_path = d.get_pdf()
    move(tmp_path, filename+".pdf")
    print("Done downloading PDF file")

if args.midi:
    tmp_path = d.get_midi()
    move(tmp_path, filename+".mid")
    print("Done downloading midi file")

print("done")
