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

# just a simplified wrapper around IPTCInfo; effectively just wrapping
# semantics for ease-of-use

import findLibs
from iptcinfo import IPTCInfo
from minimal_exif_reader import MinimalExifReader

import datetime

iptcMap = {
"copyrightNotice" : "copyright notice",
"author"          : "by-line",
"title"           : "object name",
"tags"            : "keywords", #[key1, key2, ...]
"description"     : "caption/abstract",
"dateCreated"     : "date created", #20130310
"timeCreated"     : "time created" #140658
}

def nowStamp():
  now =  datetime.datetime.today()
  date = '%04d%02d%02d' % (now.year, now.month, now.day)
  time =  '%02d%02d%02d' % (now.hour, now.minute, now.second)
  return date, time

class Image:
    def __init__(self, filename):
      self.filename = filename
      self.info = None
      self.exif = None

      try:
        self.info = IPTCInfo(self.filename, force=True)
      except:
        print "cannot initialize IPTCInfo!"
        pass

      try:
        self.exif = MinimalExifReader(self.filename)
      except:
        print "cannot initialize exif reader"
        pass

      # if we can't create either reader, give up
      if self.exif == None and self.info == None:
        print "cannot read file metadata"
        raise

      # at a minimum, we set a datestamp if one doesn't exist
      # set to current date & time
      exifDateStamp = None
      if self.exif != None:
        exifDateStamp = self.exif.dateTimeOriginal("%Y%m%d-%H%M%S")
        if exifDateStamp == "":
          exifDateStamp = None
      iptcDate = self.getData("dateCreated")
      iptcTime = self.getData("timeCreated")
  
      if exifDateStamp != None and \
        iptcDate == None and \
        iptcTime == None:
        datestamp = exifDateStamp.split('-')
        self.info.data[iptcMap['dateCreated']] = datestamp[0]
        self.info.data[iptcMap['timeCreated']] = datestamp[1]
      elif exifDateStamp == None and \
        iptcDate == None and \
        iptcTime == None:
        date, time = nowStamp()
        self.info.data[iptcMap['dateCreated']] = date
        self.info.data[iptcMap['timeCreated']] = time

    def availableFields(self):
      return iptcMap.keys()

    def setData(self, field, data):
      if field in iptcMap:
        self.info.data[iptcMap[field]] = data

    def getData(self, field):
      if self.info != None:
        if field in iptcMap:
          return self.info.data[iptcMap[field]]

      return None
 
    def writeFile(self):
      self.info.save()

    def dump(self):
      for f in self.availableFields():
        print f + " : " + str(self.getData(f))