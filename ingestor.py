import findLibs
import imagedb
import paths
import coreOpts

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

  print "adding to db..:" + str(meta)
  imagedb.imagedb.addImage(meta)
  print "GOT META: " + str(meta)
  
  print "ADDED"
  
  return meta

