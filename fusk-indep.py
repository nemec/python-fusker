#!/bin/python

import sys
import os
import urllib

usage = "Usage: fusk -u url | -f file"

if len(sys.argv) != 3:
  print usage

url=sys.argv[2];
d=0
while os.path.exists(str(d)):
  d=d+1
os.mkdir("./" + str(d) + "/")

if sys.argv[1] == "-u":
  beg = url[0:url.find('[')]
  end = url[url.find(']')+1:]
  fst = url[url.find('[')+1:url.find('-')]
  snd = url[url.find('-')+1:url.find(']')]
  try:
    for i in range(int(fst), int(snd)+1):
      pic = beg+str(i).zfill(len(snd))+end
      urllib.urlretrieve(pic, str(d)+"/"+str(i).zfill(len(snd))+end)
  except:
    urllib.retrieveurl(url, str(d)+"/"+url[url.rfind("/"):])
elif sys.argv[1] == "-f":
  with open(url, 'r') as f:
    for line in f:
      urllib.retrieveurl(line, str(d)+"/"+line[line.rfind("/"):])
  f.closed
else:
  print usage
