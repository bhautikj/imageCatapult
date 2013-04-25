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
