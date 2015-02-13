#
#  Copyright (c) 2013 Bhautik J Joshi (bjoshi@gmail.com)
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

import findLibs
import imagedb
import paths
import coreOpts
import imageGPS

import Image

import os
import shutil
import datetime
import time

#image store
imageBase = paths.imageBase
displayBase = paths.displayBase

def imageOps(imageLoc, meta):
  size = coreOpts.thumbSize, coreOpts.thumbSize
  im = Image.open(imageLoc)

  imSize = im.size
  meta["width"] = imSize[0]
  meta["height"] = imSize[1]
  
  im.thumbnail(size, Image.ANTIALIAS)
  im.save(imageLoc+".thumb.jpg", "JPEG")


def makeUnixTime(dateCreated, timeCreated):
  dt = datetime.datetime (int(dateCreated[0:4]), \
                          int(dateCreated[4:6]), \
                          int(dateCreated[6:8]), \
                          int(timeCreated[0:2]), \
                          int(timeCreated[2:4]), \
                          int(timeCreated[4:6]) )
  return int(time.mktime(dt.timetuple()))

def ingestImage(tempFile, meta):
  destDir = meta["dateCreated"]
  displayDir = os.path.join (displayBase, meta["dateCreated"])
  paths.createDir(os.path.join(imageBase,destDir))

  destFileName = os.path.join(destDir, meta["timeCreated"] + ".jpg")
  displayFileName = os.path.join(displayDir, meta["timeCreated"] + ".jpg")
  
  moveDest = os.path.join(imageBase,destFileName)
  shutil.move(tempFile, moveDest)
  
  imageOps(moveDest, meta)

  meta["dburl"] = destFileName
  meta["displayurl"] = "../" + displayFileName
  meta["unixTime"] = makeUnixTime(meta["dateCreated"], meta["timeCreated"])
  
  lat, lon = imageGPS.get_lat_lon_image(moveDest)
  meta["latitude"] = lat
  meta["longitude"] = lon

  print "adding to db..:" + str(meta)
  imagedb.imagedb.addImage(meta)
  print "GOT META: " + str(meta)
  
  print "ADDED"
  
  return meta

