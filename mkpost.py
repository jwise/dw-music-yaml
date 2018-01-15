import yaml
import sys
import re
import urllib
import os

parts = [p for p in yaml.load_all(file(sys.argv[1], "r"))]

def mangle_to_ref(album):
  orig = "%d_album_%s_%s" % (year, album["artist"], album["album"])
  return re.sub('[^a-z0-9]', '_', orig.lower())  

def stars(rating):
  rstr = ("&#x2b51;" * rating)
  if rating == 5:
    return "<span style=\"color: #ff0000\">%s</span>" % rstr
  else:
    return "<span>%s</span>" % (rstr)

for p in parts:
  if p["type"] == 'conf':
    year = p["year"]
    imgroot = p["imgroot"]
    imgpath = p["imgpath"]
  elif p["type"] == 'raw':
    print p["body"]
  elif p["type"] == 'albumsummary':
    # Look for an "albums" type thing, and summarize it.
    for p2 in parts:
      if p2["type"] == 'albums':
        for album in p2["list"]:
          print "<li><span style=\"float: left; width: 4.5em; text-align: right;\">%s&nbsp;</span> <a href=\"#%s\">%s - %s</a></li>" % \
            (stars(album["rating"]), mangle_to_ref(album), album["artist"], album["album"], )
  elif p["type"] == 'albums':
    for album in p["list"]:
      if "bandcamp" in album:
        bandcamp = "(<a href=\"%s\">bandcamp</a>) " % album["bandcamp"]
      else:
        bandcamp = ""
      
      if "cover" in album:
        fname = "%s.%s" % (mangle_to_ref(album), album["cover"].split('/')[-1].split('.')[-1])
        localpath = "%s%s" % (imgpath, fname)
        if not os.path.isfile(localpath):
          urllib.urlretrieve(album["cover"], localpath)
        cover = "<img src=\"%s%s\" style=\"float: right; width: 180px; height: 180px; margin-left: 1em; margin-bottom: 0.5em; padding: 1px; background-color: #000000;\">" % (imgroot, fname)
      else:
        cover = ""
      
      print "<li><a name=\"%s\"></a><i>%s</i>: <b><a href=\"%s\">%s%s - %s</a></b> %s(<b>%s</b>; <i>released %s</i>)." %\
        (mangle_to_ref(album), album["purchased"], album["url"], cover, album["artist"], album["album"], bandcamp, stars(album["rating"]), album["released"])
      if "short" in album:
        print "%s<br></li>" % album["short"]
      elif "body" in album:
        print "%s\n</li>" % album["body"]
      else:
        print "</li>"
  elif p["type"] == 'extracredit':
    for ent in p["list"]:
      if "short" in ent:
        print "<li><b><a href=\"%s\">%s</a></b>.  %s<br></li>" % (ent["url"], ent["title"], ent["short"])
      elif "body" in ent:
        print "<li><b><a href=\"%s\">%s</a></b>.\n%s</li>" % (ent["url"], ent["title"], ent["body"])
      else:
        print "<li><b><a href=\"%s\">%s</a></b>.</li>" % (ent["url"], ent["title"])
  elif p["type"] == 'live':
    for ent in p["list"]:
      print "<li><a href=\"%s\"><b>%s</b> at %s</a> (<i>%s</i>).  %s<br></li>" % (ent["url"], ent["act"], ent["where"], ent["date"], ent["short"])
  else:
    raise ValueError(p["type"])
