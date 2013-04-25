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
        ret.append((int(i[0]), "../imagestore/" + str(i[1])))
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
        time = 0
        if i[2] != None:
          time = int(i[2])
        ret.append((int(i[0]), "../imagestore/" + str(i[1]), int(time)))
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
      
      imagedb.setImageList(imageIds, title, description, tags, flickrSets, flickrGroups, jobDict)
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
