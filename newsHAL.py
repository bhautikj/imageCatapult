import findLibs
import feedparser
import megahal
import paths

import os

urlList = ['https://news.google.com/news/section?pz=1&cf=all&topic=snc&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&topic=tc&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&topic=w&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&topic=n&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&topic=e&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&topic=m&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&q=star+wars&output=rss&num=64',\
           'https://news.google.com/news/section?pz=1&cf=all&q=san+francisco&output=rss&num=64',\
           'https://news.google.com/news/feeds?output=rss&num=64',\
           'https://news.google.com/nwshp?hl=en&tab=nn&edchanged=1&ned=au&output=rss&num=200']          
halBrain = os.path.join(paths.appBase, 'newsHAL.brn')

newshal = megahal.MegaHAL(brainfile = halBrain, timeout = 0)

def fetchCurrentHeadlines():
  titles = []
  for url in urlList:
    d = feedparser.parse(url)
    titles.extend(map(lambda x: x.split('-', 1)[0], [entry.title for entry in d['entries']]))
  return titles

def feedHAL():
  print "FEEDING NEWSHAL... OM NOM NOM"
  for headline in fetchCurrentHeadlines():
    try:
      headlinedecode = str(headline.decode('utf-8'))
      newshal.learn(headlinedecode)
    except:
      pass
  newshal.sync()

