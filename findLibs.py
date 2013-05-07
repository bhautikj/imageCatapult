import sys
pathList = ['lib', 
           'lib/thirdparty', 
           'lib/tumblr-python', 
           'lib/DBWrapper/',
           'lib/facebook-sdk/',
           'lib/python-flickr',
           'lib/thirdparty/httplib2-0.8/python2/',
           'lib/python-oauth2/',
           'lib/python-twitter/',
           'lib/webpy/',
           'lib/wordspew/']

for path in pathList:
  if path not in sys.path:
    sys.path.append(path)
