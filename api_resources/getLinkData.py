import urllib.request, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


class Link(object):
    def __init__(self, url, title, image, source):
        self.url = url
        self.title = title
        self.image = image
        self.source = source

    def getLinkURL(self):
        return self.url

    def getLinkTitle(self):
        return self.title

    def getLinkImage(self):
        return self.image

    def getLinkSource(self):
        return self.source

def getLinkImage(linkurl, caller):
    s = linkurl
    print(s, 'looking for link in get link img function')
    parsed = urlparse(s)
    print(parsed, 'looking for parsed link in get link img function')
    parsedDict = parse_qs(parsed.query)
    print(caller, 'looking for caller in get link img function')
    print(parsedDict, 'looking for parseDict in get link img function')

    if parsedDict:
        newLink = parsedDict.get('u')[-1]
        print(newLink, "looking for parse dict link u value")
    else:
        newLink = s
        print (newLink, "looking for non-parse-dict link")

    try:
        html = urllib.request.urlopen(newLink).read()
        soup = BeautifulSoup(html, 'html.parser')
        dataImage = soup.find("meta", property="og:image")
        dataTitle = soup.find("meta", property="og:title")
        dataType = soup.find("meta", property="og:type")
        print(dataImage, 'this should be data for find meta og image')
        print(dataTitle, 'this should be data for find meta og title')
        print(dataType, 'this should be data for find meta og type')
        ## need to add some code to check if image is not blank;
        imgURL = dataImage["content"]
        linkTitle = dataTitle["content"]
        linkType = dataType["content"]
        print(imgURL, 'this should be the img URL')
        print(linkTitle, 'this should be the link title')
        print(linkType, 'this should be the link type')
        print(caller, 'looking for caller in get link img function try block')

        return imgURL, linkTitle, newLink, linkType
        ## We should return the newLink to save
    except:
        pass
