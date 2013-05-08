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
from imagedb import imagedb
from imagedb import jobColumns
from paths import imageBase
from flickrInterface import flickrObject
from facebookInterface import facebookObject
from tumblrInterface import tumblrObject
from twitterInterface import twitterObject

import web
from web import form

import os
import json
import threading
import datetime
import time


def postPendingJobs():
  jobIdList = map(lambda x: x[0], imagedb.getJobsToDo())
  for jobId in jobIdList:
    postJob(jobId)

def postJob(jobId):    
  jobData = imagedb.getJob(jobId)[0]
  jobDict = {}
  
  #TODO: imageid == jobid may not always be true
  jobDict["imageId"] = jobId
  for idx, val in enumerate(jobColumns):
    data = str(jobData[idx])
    
    if data == "None":
      data = None
      
    jobDict[val] = data
  
  #cleanup
  jobDict["fileurl"] = os.path.join(imageBase, jobDict["dburl"])
  jobDict["width"] = int(jobDict["width"])
  jobDict["height"] = int(jobDict["height"])
  jobDict["jobDict"] = json.loads(jobDict["jobDict"])
  if jobDict["tags"] != None:
    jobDict["tags"] = jobDict["tags"].split(",")
  else:
    jobDict["tags"] = []
  if jobDict["flickrSets"] != None:
    jobDict["flickrSets"] = jobDict["flickrSets"].split(",")
  if jobDict["flickrGroups"] != None:
    jobDict["flickrGroups"] = jobDict["flickrGroups"].split(",")
  jobDict["geoCode"] = int(jobDict["geoCode"])
  jobDict["latitude"] = float(jobDict["latitude"])
  jobDict["longitude"] = float(jobDict["longitude"])
    
  serviceDict = jobDict["jobDict"]
  jobStatus = {"flickr":False, "facebook": False, "tumblr": False, "twitter": False}
  serviceDict["jobStatus"] = jobStatus
  
  print serviceDict
  
  if serviceDict["flickr"] != True:
    raise Exception("need at least flickr to work!")
  else:
    if flickrObject.authorised == False:
      raise Exception("need at least flickr to work!")
    if serviceDict["jobStatus"]["flickr"] == False:
      try:
        postFlickrImage(jobDict)
        serviceDict["jobStatus"]["flickr"] = True
        imagedb.updateJobWorking(jobId, "queued", json.dumps(serviceDict))
      except:
        return
  
  if serviceDict["facebook"]:
    if facebookObject.authorised:
      if serviceDict["jobStatus"]["facebook"] == False:
        try:
          postFacebookPost(jobDict)
          serviceDict["jobStatus"]["facebook"] = True
          imagedb.updateJobWorking(jobId, "queued", json.dumps(serviceDict))
        except:
          return

  if serviceDict["tumblr"]:
    if tumblrObject.authorised:
      if serviceDict["jobStatus"]["tumblr"] == False:
        try:
          postTumblrPost(jobDict)
          serviceDict["jobStatus"]["tumblr"] = True
          imagedb.updateJobWorking(jobId, "queued", json.dumps(serviceDict))
        except:
          return

  if serviceDict["twitter"]:
    if twitterObject.authorised:
      if serviceDict["jobStatus"]["twitter"] == False:
        try:
          postTwitterPost(jobDict)
          serviceDict["jobStatus"]["twitter"] = True
          imagedb.updateJobWorking(jobId, "queued", json.dumps(serviceDict))
        except:
          return

  imagedb.updateJobWorking(jobId, "done", json.dumps(serviceDict))
  print "job complete!"

def postTwitterPost(jobDict):
  twitterObject.postImagePost(jobDict)

def postTumblrPost(jobDict):
  tumblrObject.postImagePost(jobDict)

def postFacebookPost(jobDict):
  facebookObject.postImagePost(jobDict)
  
def postFlickrImage(jobDict):
  #do it!
  try:
    photoid = flickrObject.postImage(jobDict)
  except:
    raise Exception("photo upload error, giving up")
 
  if jobDict["geoCode"] != 0:
    try:
      flickrObject.setLocation(photoid, jobDict["latitude"], jobDict["longitude"])
    except:
      print "ERROR IN SETTING LOCATION - you may need to set pref at http://www.flickr.com/account/geo/privacy/"

  try:
    flickrObject.sendToGroups(photoid, jobDict["flickrGroups"])
  except:
    print "ERROR IN SENDING TO FLICKR GROUPS"

  try:
    flickrObject.sendToSets(photoid, jobDict["flickrSets"])
  except:
    print "ERROR IN SENDING TO FLICKR SETS"
  
  try:
    sizes = flickrObject.getPhotoImageSizes(photoid)
  except:
    raise Exception("photo uploaded but can't get sizes, giving up")
  
  imagethumburl = ""
  imagelargeurl = ""
  
  for size in sizes:
    if size["label"] == "Large Square":
      imagethumburl = size["source"]
    elif size["label"] == "Large":
      imagelargeurl = size["source"]

  infoDict = flickrObject.getPhotoInfo(photoid)
  url = infoDict["urls"]["url"][0]["_content"]
  shorturl = flickrObject.getShortURL(photoid)

  jobDict["flickrurl"] = url
  jobDict["flickrshorturl"] = shorturl
  jobDict["flickrImageThumbUrl"] = imagethumburl
  jobDict["flickrImageLargeUrl"] = imagelargeurl
  
  imagedb.updateFlickrPostUpload(jobDict["imageId"], photoid, url, shorturl, imagethumburl, imagelargeurl)


## Run the job posting thread
minuteSeconds = 60
interval = 10 #runs every interval minutes

class RunJobs(threading.Thread):
  def run(self):
    while(True):
      now = datetime.datetime.now()
      print "Running pending jobs at time: %s" % (now)
      postPendingJobs()
      time.sleep(interval*minuteSeconds)

runJobsThread = RunJobs()
runJobsThread.daemon = True
runJobsThread.start()
