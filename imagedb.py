#db interface
#

import findLibs
import paths

import sqlite3
import dbwrapper.db

import os
import threading
import time
import json
import datetime, time

imagedbpath = os.path.join(paths.appBase, "image.db")
schemapath = "image.sql"
jobColumns = ["dburl","width","height","title","description","tags","flickrSets","flickrGroups","jobDict","geoCode","latitude","longitude"]

def stringWrap(text):
  if text == None:
    return None
  return "'" + text + "'"

#find the longest common substring
#see: http://stackoverflow.com/questions/2892931/longest-common-substring-from-more-than-two-strings-python
def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    elif len(data) == 1:
      substr = data[0]
    return substr

def makeDictFromRowTuples(rows):
  ret = {}
  for row in rows:
    ret[row[0]] = row[1]
  return ret

def condenseForEditor(fetchImageListColumns, rows):
  returnDict = {}
  
  colIndices = {}
  for idx, val in enumerate(fetchImageListColumns):
    colIndices[val] = idx

  #images themselves
  imageList = []
  for row in rows:
    img = {}
    img["url"] = row[colIndices["dburl"]]
    img["width"] = row[colIndices["width"]]
    img["height"] = row[colIndices["height"]]
    #imageList.append(row[db.tableColumnNames["image"]["dburl"]])
    imageList.append(img)
  returnDict["imageList"] = imageList
  
  #title
  title = ""
  titleList = []
  for row in rows:
    tmpTitle = row[colIndices["title"]]
    if tmpTitle == None:
      tmpTitle = ""
    titleList.append(tmpTitle)
  title = long_substr(titleList)
  returnDict["title"] = title
  
  #description
  description = ""
  descriptionList = []
  for row in rows:
    tmpDescription = row[colIndices["description"]]
    if tmpDescription == None:
      tmpDescription = ""
    descriptionList.append(tmpDescription)
  description = long_substr(descriptionList)
  returnDict["description"] = description

  #tags
  tags = set()
  firstRow = True
  for row in rows:
    tagCandidates = row[colIndices["tags"]]
    rowTags = set()
    if tagCandidates != None:
      for tag in tagCandidates.split(","):
        if tag != None and tag != '':
          rowTags.add(str(tag))
    if firstRow:
      firstRow = False
      tags = rowTags
    else:
      tags = tags.intersection(rowTags)

  returnDict["tags"] = list(tags)
  
  #flickr sets
  flickrSets = set()
  firstRow = True
  for row in rows:
    flickrSetCandidates = row[colIndices["flickrSets"]]
    rowFlickrSets = set()
    if flickrSetCandidates != None:
      for flickrSet in flickrSetCandidates.split(","):
        if flickrSet != None and flickrSet != '':
          rowFlickrSets.add(str(flickrSet))
    if firstRow:
      firstRow = False
      flickrSets = rowFlickrSets
    else:
      flickrSets = flickrSets.intersection(rowFlickrSets)

  returnDict["flickrSets"] = list(flickrSets)
  
  #flickr groups
  flickrGroups = set()
  firstRow = True
  for row in rows:
    flickrGroupCandidates = row[colIndices["flickrGroups"]]
    rowFlickrGroups = set()
    if flickrGroupCandidates != None:
      for flickrGroup in flickrGroupCandidates.split(","):
        if flickrGroup != None and flickrGroup != '':
          rowFlickrGroups.add(str(flickrGroup))
    if firstRow:
      firstRow = False
      flickrGroups = rowFlickrGroups
    else:
      flickrGroups = flickrGroups.intersection(rowFlickrGroups)

  returnDict["flickrGroups"] = list(flickrGroups)

  #jobDict - default is to be permissive yes
  services = ["flickr","tumblr","facebook","twitter"]
  jobServices = {}
  for service in services:
    jobServices[service] = False

  for row in rows:
    jobDict = json.loads(row[colIndices["jobDict"]])
    for service in services:
      if service in jobDict.keys():
        if jobDict[service] == True:
          jobServices[service] = True
  
  returnDict["jobDict"] =  jobServices
  
  #geoCode - default is no unless all is yes
  geoCode = True
  for row in rows:
    geoCode = row[colIndices["geoCode"]]
    if geoCode == False:
      geoCode = False
  returnDict["geoCode"] = geoCode
  
  #poupulate lat and long with first entry. not great,
  #but an average location is just silly
  row = rows[0]
  returnDict["latitude"] = row[colIndices["latitude"]]
  returnDict["longitude"] = row[colIndices["longitude"]]
  
  return returnDict

class ImageDb:
  def __init__(self, db_filename, schema_filename):
    db_is_new = not os.path.exists(db_filename)
    
    with sqlite3.connect(db_filename) as self.conn:
        if db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            self.conn.executescript(schema)
            #self.conn.close()

    #self.cursor = self.conn.cursor()
    self.db = dbwrapper.db.DBWrapper(filename=db_filename)
    self.tableColumnNames={}
    tables = self.db.get_tables()
    for table in tables:
      self.tableColumnNames[table] = self.getColumnNames(table)
    
    print "TABLES", self.tableColumnNames

  def listAllTags(self):
    exists = self.db.execute('SELECT tag, tagid FROM tag')
    if len(exists) == 0:
      return None
    return exists

  def searchTags(self, searchString):
    query = "SELECT tag FROM tag WHERE tag LIKE :tag"
    exists = self.db.execute(query, {"tag":'%'+searchString+'%'})
    if len(exists) == 0:
      return None
    return exists   

  def findTag(self, tag):
    exists = self.db.execute('select tagId from tag where tag.tag = :tag', {"tag":tag})
    if len(exists) == 0:
      return None
    return exists[0][0]

  def addTag(self, tag):
    exists = self.db.execute('select * from tag where tag.tag = :tag', {"tag":tag})
    if len(exists) == 0:
      self.db.execute('INSERT INTO tag(tag) values (:tag)', {"tag":tag})
    self.db.commit()

  def addTags(self, tags):
    tagIdList = []
    for tag in tags:
      self.addTag(tag)
      tagIdList.append(self.findTag(tag))
    return tagIdList

  def getColumnNames(self, tableName):
    query =  "PRAGMA table_info(" + tableName + ");"
    headers = self.db.execute(query)
    names = {}
    idx = 0
    for head in headers:
      names[head[1]] = idx
      idx += 1
    return names
    
  def findImage(self, meta):
    print "finding image.."
    exists = self.db.execute('select imageId from image where\
                         image.unixTime = :unixTime',
                         {"unixTime": int(meta["unixTime"])})
    print "cursorfech done"
    if len(exists) == 0:
      return None
    return exists[0][0]

  def deleteImageList(self, ids):
    #get filenames
    query= 'SELECT dburl FROM image WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
    exists = self.db.execute(query)
    if len(exists) == 0:
      return
    imagesToDelete = map(lambda x: x[0], exists)
    
    query= 'DELETE FROM image WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
    self.db.execute(query)
    query= 'DELETE FROM job WHERE job.imageId IN (' + ','.join(map(str, ids)) + ')'
    self.db.execute(query)
    query= 'DELETE FROM flickrImage WHERE flickrImage.imageId IN (' + ','.join(map(str, ids)) + ')'
    self.db.execute(query)
    
    for image in imagesToDelete:
      delpath = os.path.join(paths.imageBase, image)
      try:
        os.remove(delpath)
        os.remove(delpath + ".thumb.jpg")
      except:
        print "unable to delete file: " + str(delpath)
        pass
    

  def fetchImageList(self, fetchImageListColumns, ids):    
    cols = ",".join(fetchImageListColumns)
    query= 'SELECT ' + cols + ' FROM image NATURAL JOIN flickrImage, job WHERE image.imageId = job.imageId AND image.imageId IN (' + ','.join(map(str, ids)) + ')'
    #image.imageId = job.imageId AND image.imageId = flickr.imageId AND 
    exists = self.db.execute(query)
    return exists

  def setImageList(self, ids, title, description, tags, flickrSets, flickrGroups, jobDict, geoCode, latitude, longitude):
    if title != None:
      query = 'UPDATE image SET title=:title WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"title":title})
    if description != None:
      query = 'UPDATE image SET description=:description WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"description":description})

    if tags != None:
      tagString = ','.join(tags)
      self.addTags(tags)
      query = 'UPDATE image SET tags=:tags WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"tags":tagString})
    
    if flickrSets != None:
      query = 'UPDATE flickrImage SET flickrSets=:flickrSets WHERE flickrImage.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query,{"flickrSets":",".join(flickrSets)})

    if flickrGroups != None:
      query = 'UPDATE flickrImage SET flickrGroups=:flickrGroups WHERE flickrImage.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query,{"flickrGroups":",".join(flickrGroups)})
      
    if jobDict != None:
      jobDictString = json.dumps(jobDict)
      query = 'UPDATE job SET jobDict=:jobDict WHERE job.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"jobDict":jobDictString})

    if geoCode != None:
      query = 'UPDATE image SET geoCode=:geoCode WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"geoCode":geoCode})

    if latitude != None:
      query = 'UPDATE image SET latitude=:latitude WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"latitude":latitude})
      
    if longitude != None:
      query = 'UPDATE image SET longitude=:longitude WHERE image.imageId IN (' + ','.join(map(str, ids)) + ')'
      self.db.execute(query, {"longitude":longitude})
      
    self.db.commit()

  def fetchEditorDict(self, imageList):
    fetchImageListColumns = jobColumns
    rows = self.fetchImageList(fetchImageListColumns, imageList)
    return condenseForEditor(fetchImageListColumns, rows)

  def addImage(self, meta):
    print "adding image..."
    if self.findImage(meta) != None:
      print "IMAGE ALREADY ADDED"
      return
    print "image not found"
    
    services = ["flickr","tumblr","facebook","twitter"]
    jobDict = {}
    for service in services:
      jobDict[service] = True
    
    jobDictString = json.dumps(jobDict)
    
    tagsString = ""
    if "tags" in meta.keys():
      if meta["tags"] != None:
        for tag in meta["tags"]:
          self.addTag(tag)
        tagsString = ",".join(meta["tags"])
    
    #placeholders until the ingestor supports geo
    geoCode = False
    latitude = 0
    longitude = 0

    imageTuple = (meta["copyrightNotice"],\
                  meta["author"],\
                  meta["title"],\
                  meta["dburl"],\
                  meta["description"],\
                  meta["size"],\
                  meta["width"],\
                  meta["height"],\
                  meta["unixTime"],\
                  tagsString,
                  geoCode,
                  latitude,
                  longitude)
    self.db.execute('insert into image(copyrightNotice,\
                                           author,\
                                           title,\
                                           dburl,\
                                           description,\
                                           imagesize,\
                                           width,\
                                           height,\
                                           unixTime,\
                                           tags,\
                                           geoCode,\
                                           latitude,\
                                           longitude) values (?,?,?,?,?,?,?,?,?,?,?,?,?)',\
                                           imageTuple)
    
    imageId = self.findImage(meta)
    
    query = 'INSERT INTO flickrImage(imageId) values (:imageId)'
    self.db.execute(query, {"imageId":imageId})
      
    query = "INSERT INTO job(imageId, status, jobDict) values (:imageId,'pending', :jobDict)"
    self.db.execute(query, {"jobDict":jobDictString, "imageId":imageId} )

    self.db.commit()

  def listAllImages(self, minDate=None, maxDate=None):
    query = 'SELECT imageId, dburl FROM image '
    if minDate != None:
      query += ' WHERE unixTime > ' + str(minDate)
    if minDate != None and maxDate != None:
      query += ' AND '
    if minDate == None and maxDate != None:
      query += ' WHERE '
    if maxDate != None:
      query += ' unixtime < ' + str(maxDate)
 
    query += ' ORDER BY unixTime ASC '

    exists = self.db.execute(query)
    if len(exists) == 0:
      return None
    return exists

  def addJob(self, imageId, jobTime, jobDict, status="pending"):
    query = 'INSERT INTO job(imageId, jobTime, jobDict, status) values (?, ?, ?, ?)'
    jobTuple = (imageId, jobTime, jobDict, status)
    self.db.execute(query, jobTuple)
    self.db.commit()
    
  def updateJob(self, imageId, status, jobTime, jobDict=None):
    if jobTime == None and jobDict == None:
      return
    
    paramsDict = {"imageId": imageId, "status": status}
    
    query = 'UPDATE job SET status = :status, '
    query += ' jobTime=:jobTime '
    paramsDict["jobTime"] = jobTime

    if jobDict != None:
      query += ' jobDict=:jobDict '
      paramsDict["jobDict"] = jobDict
      
    query += ' WHERE imageId=:imageId'
    self.db.execute(query, paramsDict)
    self.db.commit()

  def updateJobWorking(self, imageId, status, jobDict):    
    paramsDict = {"imageId": imageId, "status": status, "jobDict": jobDict}
    
    query = 'UPDATE job SET status = :status, '
    query += ' jobDict=:jobDict '      
    query += ' WHERE imageId=:imageId'
    self.db.execute(query, paramsDict)
    self.db.commit()

  def listAllJobs(self, status, minDate=None, maxDate=None):
    query = "SELECT imageId, dburl, jobTime FROM image NATURAL JOIN job WHERE image.imageId = job.imageId AND status = :status"
    if minDate != None and maxDate != None:
      query += ' AND jobTime > ' + str(minDate) + ' AND jobTime < ' + str(maxDate)
 
    query += ' ORDER BY jobTime ASC '

    exists = self.db.execute(query, {"status":status} )
    if len(exists) == 0:
      return None
    return exists
  
  def getJobsToDo(self):
    now = int(time.mktime(datetime.datetime.now().timetuple()))
    query = "SELECT imageId FROM job WHERE jobTime < :now AND status = 'queued'"
    exists = self.db.execute(query, {"now":now})
    if len(exists) == 0:
      return []
    return exists 
  
  def getJob(self, jobId, fetchImageListColumns=jobColumns):
    cols = ",".join(fetchImageListColumns)
    query= 'SELECT ' + cols + ' FROM image NATURAL JOIN flickrImage, job WHERE image.imageId = job.imageId AND job.imageId = :jobId'
    exists = self.db.execute(query, {"jobId":jobId})
    return exists
  
  def getMinImageDate(self):
    exists = self.db.execute('SELECT MIN(unixTime) FROM image')
    if len(exists) == 0:
      return None
    return exists[0][0]
  
  def getMaxImageDate(self):
    exists = self.db.execute('SELECT MAX(unixTime) FROM image')
    if len(exists) == 0:
      return None
    return exists[0][0]
  
  def getAllTemplateNames(self):
    exists = self.db.execute('SELECT templateId, name FROM template')
    if len(exists) == 0:
      return None
    return exists
  
  def addTemplate(self, name, templateDict):
    exists = self.db.execute('SELECT * FROM template WHERE template.name = :name', {"name":name})
    if len(exists) == 0:
      self.db.execute('INSERT INTO template(name,dict) values (:name, :templateDict)', {"name":name, "templateDict":templateDict})
    else:
      self.db.execute('UPDATE template SET dict=:templateDict WHERE name=:name', {"name":name, "templateDict":templateDict})
    self.db.commit()    
  
  def getTemplate(self, templateId):
    exists = self.db.execute('SELECT dict FROM template WHERE template.templateId = :templateId', {"templateId":templateId})
    if len(exists) == 0:
      return None
    return exists
  
  def populateFlickrSets(self, sets):
    self.db.execute('DELETE FROM flickrSets')
    for set in sets.keys():
      self.db.execute('INSERT INTO flickrSets(id,name) values (:id, :name)', {"id":set, "name":sets[set]})
    self.db.commit() 

  def populateFlickrGroups(self, groups):
    self.db.execute('DELETE FROM flickrGroups')
    for group in groups.keys():
      self.db.execute('INSERT INTO flickrGroups(nsid,name) values (:nsid, :name)', {"nsid":group, "name":groups[group]})
    self.db.commit() 
  
  def getFlickrSets(self):
    exists = self.db.execute('SELECT id,name FROM flickrSets')
    if len(exists) == 0:
      return {}
    else:
      return makeDictFromRowTuples(exists)

  def getFlickrGroups(self):
    exists = self.db.execute('SELECT nsid,name FROM flickrGroups')
    if len(exists) == 0:
      return {}
    else:
      return makeDictFromRowTuples(exists)

  def updateFlickrPostUpload(self, imageId, photoId, url, shorturl, imagethumburl, imagelargeurl):
    query = 'UPDATE flickrImage SET url=:url, shorturl=:shorturl, photoId=:photoId, imageThumbUrl=:imageThumbUrl, imageLargeUrl=:imageLargeUrl WHERE imageId=:imageId'
    paramsDict = {}
    paramsDict["imageId"] = imageId
    paramsDict["photoId"] = photoId
    paramsDict["url"] = url
    paramsDict["shorturl"] = shorturl
    paramsDict["imageThumbUrl"] = imagethumburl
    paramsDict["imageLargeUrl"] = imagelargeurl
    self.db.execute(query, paramsDict)
    self.db.commit()
    
imagedb = ImageDb(imagedbpath, schemapath)

