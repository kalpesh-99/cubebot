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
        try:
            newLink = parsedDict.get('u')[-1]
            print(newLink, "looking for parse dict link u value")
            html = urllib.request.urlopen(newLink).read()
            # print(html, 'this should be the html')
            soup = BeautifulSoup(html, 'html.parser')
            # print(soup, 'this should be the html soup')
            data = soup.find("meta", property="og:image")
            print(data, 'this should be data for find meta og image')
            ## need to add some code to check if image is not blank;
            imgURL = data["content"]
            print(imgURL, 'this should be the img URL')
            print(caller, 'looking for caller in get link img function try block')

            return imgURL
            ## We should return the newLink to save
        except:
            pass
    else:
        html = urllib.request.urlopen(s).read()
        # print(html, 'this should be the html')
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup, 'this should be the html soup')
        data = soup.find("meta", property="og:image")
        print(data, 'else, this should be data for find meta og image')
        ## need to add some code to check if image is not blank;
        imgURL = data["content"]
        print(imgURL, 'else, this should be the img URL')
        print(caller, 'else, looking for caller in get link img function try block')

        return imgURL
