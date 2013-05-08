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
import authPickler
from apiToolsBase import OAuthObjectBase
from apiToolsBase import redirectToUrlText
from imagedb import imagedb

import web
from web import form

from flickr import FlickrAPI

import json

class FlickrObject(OAuthObjectBase):
  def __init__(self):
    OAuthObjectBase.__init__(self)
    self.apiName = "flickr"

  def authPart1(self):
    f = FlickrAPI(api_key=self.api_key,
            api_secret=self.api_secret,
            callback_url= web.ctx.homedomain + '/auth/flickrAuth?')

    auth_props = f.get_authentication_tokens(perms='write')
    auth_url = auth_props['auth_url']

    #Store this token in a session or something for later use in the next step.
    self.oauth_token = auth_props['oauth_token']
    self.oauth_token_secret = auth_props['oauth_token_secret']

    return auth_url

  def authPart2(self, oauth_token, oauth_verifier):
    f = FlickrAPI(api_key=self.api_key,
        api_secret=self.api_secret,
        oauth_token=self.oauth_token,
        oauth_token_secret=self.oauth_token_secret)

    authorised_tokens = f.get_auth_tokens(oauth_verifier)

    self.final_oauth_token = authorised_tokens['oauth_token']
    self.final_oauth_token_secret = authorised_tokens['oauth_token_secret']

    authDict = authPickler.getAuthDict(self.apiName)
    authDict["final_oauth_token"] = self.final_oauth_token
    authDict["final_oauth_token_secret"] = self.final_oauth_token_secret
    authPickler.setAuthDict(self.apiName, authDict)
    self.authorised = True

    self.setupAPI()

    return redirectToUrlText(web.ctx.homedomain)

  def setupAPI(self):
    self.flickrAPI = FlickrAPI(api_key=self.api_key,
                    api_secret=self.api_secret,
                    oauth_token=self.final_oauth_token,
                    oauth_token_secret=self.final_oauth_token_secret)

  def getGroups(self, params=None):
    try:
      firstQuery = self.flickrAPI.get("flickr.groups.pools.getGroups", params)
      nPages = firstQuery["groups"]["pages"]
      groupList = []
      if nPages > 0:
        groupList += firstQuery["groups"]["group"]
      if nPages > 1:
        paramPerPage = params
        for pageNum in range(2, nPages+1):
          paramPerPage["page"] = pageNum
          pageQuery = self.flickrAPI.get("flickr.groups.pools.getGroups", params)
          groupList += pageQuery["groups"]["group"]
        
      retDict = {}
      for group in groupList:
        retDict[group["nsid"]] = group ["name"]
      imagedb.populateFlickrGroups(retDict)
    except:
      pass
  
  def getSets(self, params=None):
    try:
      firstQuery = self.flickrAPI.get("flickr.photosets.getList", params)
      nPages = firstQuery["photosets"]["pages"]
      setList = []
      if nPages > 0:
        setList += firstQuery["photosets"]["photoset"]
      if nPages > 1:
        paramPerPage = params
        for pageNum in range(2, nPages+1):
          paramPerPage["page"] = pageNum
          pageQuery = self.flickrAPI.get("flickr.photosets.getList", params)
          setList += pageQuery["photosets"]["photoset"]
        
      retDict = {}
      for pset in setList:
        retDict[pset["id"]] = pset ["title"]["_content"]
      imagedb.populateFlickrSets(retDict)
    except:
      pass

  def postImage(self, jobDict):
    imageLoc = jobDict["fileurl"]
    
    paramsDict = {}
    if jobDict["title"] != None:
      paramsDict["title"] = jobDict["title"]
    if jobDict["description"] != None:
      paramsDict["description"] = jobDict["description"]
    if jobDict["tags"] != []:
      paramsDict["tags"] = ' '.join(map(lambda y: '"' + y + '"', jobDict["tags"]))
    
    print "jobDict", jobDict
    print "paramsDict", paramsDict
    
    
    files = open(imageLoc, 'rb')
    add_photo = self.flickrAPI.post(params=paramsDict, files=files)

    #print "PHOTO_ID", add_photo["photoid"]
    
    if add_photo["stat"] != "ok":
      raise Exception("Photo failed to upload, flickr did not return ok stat")

    return add_photo["photoid"]

  def setLocation(self, photoId, latitude, longitude):
    params = {"photo_id":photoId, "lat":latitude, "lon":longitude}
    result = self.flickrAPI.get("flickr.photos.geo.setLocation", params)
    
  def sendToGroups(self, photoId, groupList):
    if groupList == None:
      return

    for group in groupList:
      params = {"photo_id":photoId, "group_id":group}
      result = self.flickrAPI.get("flickr.groups.pools.add", params)
      if result["stat"] != "ok":
        print "error adding photo " + photoId + " to group " + group 

  def sendToSets(self, photoId, setList):
    if setList == None:
      return

    for flickrSet in setList:
      params = {"photo_id":photoId, "photoset_id":flickrSet}
      result = self.flickrAPI.get("flickr.photosets.addPhoto", params)
      if result["stat"] != "ok":
        print "error adding photo " + photoId + " to set " + flickrSet 
  
  def getPhotoInfo(self, photoId):
    params = {"photo_id":photoId}
    result = self.flickrAPI.get("flickr.photos.getInfo", params)
    if result["stat"] != "ok":
      print "cannot get photo info for photo " + photoId
      
    return result["photo"]
  
  def getShortURL(self, photoId):
    num=int(photoId)
    a='123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    bc=len(a)
    enc=''
    while num>=bc:
        div,mod=divmod(num,bc)
        enc = a[mod]+enc
        num = int(div)
    enc = a[num]+enc
    return "http://flic.kr/p/" + enc 

  def getPhotoImageSizes(self, photoId):
    params = {"photo_id":photoId}
    result = self.flickrAPI.get("flickr.photos.getSizes", params)
    if result["stat"] != "ok":
      print "cannot get photo info for photo " + photoId
      
    return result["sizes"]["size"]

#-------------------------------------------------------------------------------

flickrObject = FlickrObject()
flickrObject.setup()
flickrObject.getSets()
flickrObject.getGroups()

authUrls = (
"", "FlickrAuth",
)

render = web.template.render('templates/')

class FlickrAuth:
  def GET(self, path=None):
    global flickrObject

    if not flickrObject.authorised:
      params  = web.input()
      if 'oauth_token' in params.keys() and 'oauth_verifier' in params.keys():
        return flickrObject.authPart2(params['oauth_token'], params['oauth_verifier'])

  def POST(self):
    params = web.input()
    global flickrObject
    if "submitInitial" in params.keys():
      apiKey = params["apiKey"]
      apiSecret = params["apiSecret"]
      
      flickrObject.setupApp(apiKey, apiSecret)
      redirectURL =  flickrObject.authPart1()

      return json.dumps({'redirectURL':redirectURL})
 

flickrAuthApp = web.application(authUrls, locals())

urls = (
"", "FlickrApp",
)

class FlickrApp:
  def GET(self):
    params = web.input()
    numParams = len(params.keys())
    if "getSets" in params.keys():
      return json.dumps(imagedb.getFlickrSets())
    elif "getGroups" in params.keys():
      return json.dumps(imagedb.getFlickrGroups())
    elif "authorised" in params.keys():
      return json.dumps(flickrObject.authorised)

flickrApp = web.application(urls, locals())