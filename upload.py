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
from imageInfo import Image
import tempfile
import ingestor

import web
import json

urls = ('', 'Upload')

# Response dict should be something like:
#"name": "picture1.jpg",
#"size": 902604,
#"url": "http:\/\/example.org\/files\/picture1.jpg",
#"thumbnail_url": "http:\/\/example.org\/files\/thumbnail\/picture1.jpg",
#"delete_url": "http:\/\/example.org\/files\/picture1.jpg",
#"delete_type": "DELETE"

def assembleJsonResponse(metaDict):
  rv = {}
  rv["files"] = [metaDict]
  jsonDump = json.dumps(rv)
  return jsonDump

class Upload:
    def GET(self):
        return """<html><head></head><body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile" />
<br/>
<input type="submit" />
</form>
</body></html>"""

    def POST(self):
        x = web.input()
        #try:
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(x['files[]'])
        f.close()
        print "creating image"
        image = Image(f.name)
        metaDict = {}
        for k in image.availableFields():
          metaDict[k] = image.getData(k)
        metaDict['size'] = len(x['files[]'])
        #pass this to the ingestor
        metaDict = ingestor.ingestImage(f.name, metaDict)
        return assembleJsonResponse(metaDict)


uploadApp = web.application(urls, locals())
