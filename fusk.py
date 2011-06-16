#!/usr/bin/python

# This program can take a url in the form www.example.com/photo/pic[0-9].jpg
# and expand it to 10 different urls or it will read a file containing a list
# of urls then it will download the data at those urls into a numerically
# sequential folder.
# Notes:
#   Only one set of [] are possible in this version, and there is no error
#     checking to make sure there is a matching bracket.
#   Ranges can only be numbers, no letters in this version.
#   A range from [0-10] translates to 00, 01, 02, etc.

import sys
import os
import urllib2
import Queue
import argparse
import threading
  
parser = argparse.ArgumentParser(description = "Takes a url of the form "
                      "www.example.com/photos/pic[0-9].jpg and expands it.")
parser.add_argument("-p", "--pad", default="", type = lambda x: x[0:1],
                      help = "Single character to pad "
                      "short expansions with. [0-10] becomes 00, 01, etc. "
                      "with a padding of \"0\". Defaults to no padding.")
parser.add_argument("-d", "--dest", default=".", help="Destination to place the"
                                                " folder containing the files.")
parser.add_argument("-t", "--threads", default = 1, type = int,
                    help = "Number of threads.")
parser.add_argument("-q", "--quiet", action = "store_true")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-u", "--url", help = "URL to expand")
group.add_argument("-f", "--file", help = "File containing a list of URLs to "
                                          "download.")
                                          
args = parser.parse_args()

def expand(url):
  parts = []
  try:
    ssub = url.find('[')
    msub = url.find('-',ssub)
    esub = url.find(']',msub)
    beg = url[0:ssub]
    end = url[esub+1:]
    fst = url[ssub+1:msub]
    snd = url[msub+1:esub]
    for i in range(int(fst), int(snd)+1):
      if args.pad:
        pic = str(i).rjust(len(snd), args.pad)
      else:
        pic = str(i)
      parts.append(beg+pic)
  except ValueError:
    pass
    
  files = []
  for f in parts:
    for rest in expand(end):
      files.append(f + rest)
      
  return files or [url]

def get_next_dir(dest):
  d=0
  while os.path.exists(str(d)):
    d=d+1
  return str(d)
destination_dir = os.path.join(args.dest, get_next_dir(args.dest))
os.mkdir(destination_dir)

def thread_work(files, dest_dir):
  while True:
    url = files.get()
    try:
      if not args.quiet:
        print "Downloading {} to {}".format(url, dest_dir)
      try:
        filepath = os.path.join(destination_dir, url[url.rfind(os.sep):])
        filename = filepath[filepath.rfind(os.sep):]
        request = urllib2.urlopen(url)
        f = open(os.path.join(dest_dir) + filename, 'wb')
        f.write(request.read())
        f.close()
      except urllib2.HTTPError as e:
        if e.code == 404:
          print "404: {} does not exist on the server.".format(url)
    finally:
      files.task_done()
  return
      

files = Queue.Queue()

if args.url:
  for url in expand(args.url):
    files.put(url)
elif args.file:
  with open(args.file, 'r') as f:
    for line in f:
      files.append(line)
  f.close()
  
threads = []
for x in range(min(args.threads, files.qsize())):
  newthread = threading.Thread(target = thread_work, args = (files, destination_dir))
  newthread.daemon = True
  threads.append(newthread)
  newthread.start()

files.join()
