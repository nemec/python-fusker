#!/bin/python

# This program can take a url in the form www.example.com/photo/pic[0-9].jpg
# and expand it to 10 different urls or it will read a file containing a list
# of urls then it will download the data at those urls into a numerically
# sequential folder.
# Notes:
#   Only one set of [] are possible in this version, and there is no error
#     checking to make sure there is a matching bracket.
#   Ranges can only be numbers, no letters in this version.
#   A range from [0-10] translates to 00, 01, 02, etc.

# If true, uses urllib instead of Linux's native wget
# I should probably get rid of wget and make it always independent,
# but wget is just so simple!
independent = True

import sys
import os
if independent:
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
      # Don't pad with zeroes
      # pic = str(i)
      pic = str(i).zfill(len(snd))
      if independent:
        urllib.urlretrieve(beg+pic, str(d)+"/"+pic+end)
      else:
        os.system("wget -P"+str(d)+" "+beg+pic+end)
  except:
    if independent:
      urllib.retrieveurl(url, str(d)+"/"+url[url.rfind("/"):])
    else:
      os.system("wget -P"+str(d)+" "+url)
elif sys.argv[1] == "-f":
  with open(url, 'r') as f:
    for line in f:
      if independent:
        urllib.retrieveurl(line, str(d)+"/"+line[line.rfind("/"):])
      else:
        os.system("wget -P"+str(d)+" "+line)
  f.closed
else:
  print usage
