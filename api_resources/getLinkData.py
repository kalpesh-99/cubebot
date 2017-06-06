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

def getLinkImage(linkurl):
    s = linkurl
    parsed = urlparse(s)
    parsedDict = parse_qs(parsed.query)
    newLink = parsedDict.get('u')[-1]

    html = urllib.request.urlopen(newLink).read()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find("meta", property="og:image")
    imgURL = data["content"]

    return imgURL
