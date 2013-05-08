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

import web
from web import form

import json


urls = (
"", "ImagedbInteraface",
)

render = web.template.render('templates/')

class ImagedbInteraface:
  def GET(self, path=None):
    params = web.input()
    numParams = len(params.keys())
    if "imageList" in params.keys():
      minDate = None
      maxDate = None
      if "minDate" in params.keys():
        minDate = params["minDate"]
      if "maxDate" in params.keys():
        maxDate = params["maxDate"]
      dbList = imagedb.listAllImages(minDate=minDate, maxDate=maxDate)
      ret = []
      if dbList == None:
        return json.dumps(ret)
      
      for i in dbList:
        #image ID, image URL, status, jobtime, unixtime
        entry = (int(i[0]), "../imagestore/" + str(i[1]), str(i[2]), str(i[3]), str(i[4])) 
        ret.append(entry)
      return json.dumps(ret)
    elif "jobList" in params.keys():
      minDate = None
      maxDate = None
      if "minDate" in params.keys():
        minDate = params["minDate"]
      if "maxDate" in params.keys():
        maxDate = params["maxDate"]
      status = params["status"]
      dbList = imagedb.listAllJobs(status, minDate=minDate, maxDate=maxDate)
      ret = []
      if dbList == None:
        return json.dumps(ret)
      
      for i in dbList:
        #image ID, image URL, status, jobtime, unixtime
        entry = (int(i[0]), "../imagestore/" + str(i[1]), str(i[2]), str(i[3]), str(i[4])) 
        ret.append(entry)
      return json.dumps(ret)
    elif "getImageDateRange" in params.keys():
      minDate = imagedb.getMinImageDate()
      maxDate = imagedb.getMaxImageDate()
      return json.dumps([minDate, maxDate])

      
    
  def POST(self):
    params = web.input()
    numParams = len(params.keys())
    
    if "selectedList" in params.keys():
      imageIdsString = params["selectedList"]
      imageIds = json.loads(imageIdsString)
      editorDict = imagedb.fetchEditorDict(imageIds)
      for i in range(0,len(editorDict["imageList"])):
        editorDict["imageList"][i]["url"] = "../imagestore/" + editorDict["imageList"][i]["url"]
      return json.dumps(editorDict)
    elif "deleteImagesList" in params.keys():
      deleteImagesList = params["deleteImagesList"]
      imageIds = json.loads(deleteImagesList)
      imagedb.deleteImageList(imageIds)
    elif "submitList" in params.keys():
      imageIdsString = params["submitList"]
      imageIds = json.loads(imageIdsString)
      title = None
      description = None
      tags = None
      flickrSets = None
      flickrGroups = None
      jobDict = None
      geoCode = None
      latitude = None
      longitude = None

      print params
      
      if "title" in params.keys():
        title = json.loads(params["title"])
      if "description" in params.keys():
        description = json.loads(params["description"])
      if "tags" in params.keys():
        tags = json.loads(params["tags"])
      if "flickrSets" in params.keys():
        flickrSets = json.loads(params["flickrSets"])
      if "flickrGroups" in params.keys():
        flickrGroups = json.loads(params["flickrGroups"])
      if "jobDict" in params.keys():
        jobDict = json.loads(params["jobDict"])
      if "geoCode" in params.keys():
        geoCode = json.loads(params["geoCode"])
      if "latitude" in params.keys():
        latitude = json.loads(params["latitude"])
      if "longitude" in params.keys():
        longitude = json.loads(params["longitude"])
      
      
      imagedb.setImageList(imageIds, title, description, tags, flickrSets, flickrGroups, jobDict, geoCode, latitude, longitude)
      return json.dumps([])
    elif 'queueJob' in params.keys():
      imageId = params["imageId"]
      status =  params["status"]
      jobTime = params["jobTime"]
      print "PARAMS FOR JOB SUBMIT", params
      imagedb.updateJob(imageId, status, jobTime);
      #updateJob(self, imageId, status, jobTime, jobDict=None):
    return json.dumps(None)

imagedbApp= web.application(urls, locals())
