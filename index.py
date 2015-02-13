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
from authPage import authApp
from upload import uploadApp
from imagedbWeb import imagedbApp
from tagsWeb import tagsApp
from templateWeb import templateApp
from flickrInterface import flickrApp
from wordspewWeb import wordspewApp
import paths
import job

import web
import urllib
import posixpath
import os

urls = (
  '/auth', authApp,
  '/upload', uploadApp,
  '/image', imagedbApp,
  '/tags', tagsApp,
  '/template', templateApp,
  '/flickr', flickrApp,
  '/spew', wordspewApp,
  '/', 'index'
)

render = web.template.render('templates/')

class Index:   
  def GET(self, path):
    return "INDEX"

app = web.application(urls, locals())

class index:
  def GET(self):
    # redirect to the static file ...
    raise web.seeother('/static/index.html')
      
class RoutingApp(web.httpserver.StaticApp):
  def __init__(self, environ, start_response, prefixDict):
    web.httpserver.StaticApp.__init__(self, environ, start_response)
    self.prefixDict = prefixDict
    
    for key in prefixDict.keys():
      destPath = prefixDict[key]
      if destPath == None or len(destPath) == 0:
        raise Exception("Path mapping for " + key + " cannot be null")
      elif destPath[0] == '/':
        raise Exception("Path mapping for " + key + " to " + destPath + "cannot start with a /")

  def translate_path(self, path):
    root = os.getcwd()
    for prefix in self.prefixDict.keys():
      if path.startswith(prefix):
        rootPath = os.path.join(root, self.prefixDict[prefix])
        fullPath = os.path.join(rootPath, web.lstrips(path,prefix))
        return fullPath

    result = web.httpserver.StaticApp.translate_path(self, path)
    return result
    
class StaticMiddleware:
  def __init__(self, app, prefixDict={"/static/":"/static/"}):
    self.app = app
    self.prefixDict = prefixDict
  
  def __call__(self, environ, start_response):
    path = environ.get('PATH_INFO', '')
    path = self.normpath(path)

    for prefix in self.prefixDict.keys():
      if path.startswith(prefix):
        return RoutingApp(environ, start_response, prefixDict)

    return self.app(environ, start_response)
  
  def normpath(self, path):
    path2 = posixpath.normpath(urllib.unquote(path))
    if path.endswith("/"):
      path2 += "/"
    return path2

if __name__ == "__main__":
    relpath = os.path.relpath(paths.imageBase)
    prefixDict = {}
    prefixDict["/imagestore/"] = relpath
    prefixDict["/static/"] = "static/"

    wsgifunc = app.wsgifunc()
    wsgifunc = StaticMiddleware(wsgifunc, prefixDict=prefixDict)
    wsgifunc = web.httpserver.LogMiddleware(wsgifunc)

    server = web.httpserver.WSGIServer(("0.0.0.0", 8080), wsgifunc)
    print "http://%s:%d/" % ("0.0.0.0", 8080)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

