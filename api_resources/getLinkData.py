import urllib.request, re
from urllib.request import Request, urlopen, HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from time import sleep
import urllib.request as urlRequest
import urllib.parse as urlParse
# from urllib.request import urlopen


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
    print("TESTING WE GET HERE?")
    print(s, 'looking for link in get link img function')
    parsed = urlparse(s)
    print(parsed, 'looking for parsed link in get link img function')
    print("TESTING PRE-PARSE_QS")

    parsedDict = parse_qs(parsed.query)
    print(caller, 'looking for caller in get link img function')
    print(parsedDict, 'looking for parseDict in get link img function')
    print("TESTING LINK PARSE")

    if parsedDict is not None:
        newLink = parsedDict.get('u')[-1]
        print(newLink, "looking for parse dict link u value")
    elif parsedDict == {}:
        print("we can't use parsed data")
        newLink = s
    else:
        newLink = s
        print(newLink, "looking for non-parse-dict link")
        
    return getLinkContent(newLink, caller)


def getLinkContent(newLink, caller):
    caller = caller
    print(caller)
    parseNewLink = urlparse(newLink)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parseNewLink)
    domainName = parseNewLink.netloc

    print(parseNewLink, "looking @ new link parse data")
    print(domain, "looking @ domain of new link")
    print(domainName, "looking domain name of new link")


    print("pre Request this worked??")
    # adding headers has helped to avoid 403 errors
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}

    try:
        req = urlRequest.Request(newLink, headers = headers)
        print("post Request this worked??")
        openReq = urlRequest.urlopen(req)
        sourceCode = openReq.read()

        print("post html urlOpenReq this worked??")

        print(openReq.getcode())

        soup2 =BeautifulSoup(sourceCode, "html.parser")
        # print(soup2, "did we get soup object?")

        dataImage = soup2.find("meta", property="og:image")
        dataTitle = soup2.find("meta", property="og:title")
        dataType = soup2.find("meta", property="og:type")
        altDataImage = soup2.find("img", id="cover-img") #check alt image source for spotify links
        faviconDataImage = soup2.find("link", rel="icon") #check for favicon

        print(dataImage, "did we get img tag?")
        print(dataTitle, "did we get title tag?")
        print(dataType, "did we get type tag?")
        print(altDataImage, "did we get alt img tag?")
        print(faviconDataImage, "did we get alt img tag?")

        if dataImage == None: #this case = spotify open links didn't have og:imgage
            if altDataImage:
                altImgURL = altDataImage["src"]
                imgURLCheck = urlparse(altImgURL) #this case = spotify uses some unique link with no https or .jpeg
                print(imgURLCheck, "url parse for alt image")
                parsedDict_imgURLCheck = parse_qs(imgURLCheck.scheme)
                print(parsedDict_imgURLCheck, "scheme check?")
                if parsedDict_imgURLCheck == {}:
                    imgURL = "https:" +altImgURL
                    print(imgURL, "added https for alt image?")
                else:
                    imgURL = altImgURL
            else:
                imgURL = "generic"
                # imgURL = domain
                print(imgURL, "test if domain = img url")
            # elif faviconDataImage:
            #     if not altDataImage:
            #         print("testing if favicon exists and no alt data image")
            #         faviconURL =  faviconDataImage["href"]
            #         print(faviconURL, "testing to see fav icon url")
        else:
            imgURL = dataImage["content"]
            try:
                imageLinkTest = urllib.urlopen(urllib.Request(imgURL))
                deadLinkFound = False
                print(deadLinkFound, 'LOOKING @ IMAGE LINK TEST')
            except:
                deadLinkFound = True
                print(deadLinkFound, 'LOOKING @ IMAGE LINK TEST')
        # else:
        #     # imgURL = "generic"
        #     imgURL = domain

        if dataTitle != None:
            linkTitle = dataTitle["content"]
        else:
            if caller == "webform":
                linkTitle = "{domainName}".format(domainName=domainName)
            else:
                linkTitle = "generic"

        if dataType != None:
            linkType = dataType["content"]
        else:
            linkType = "Website"

        return imgURL, linkTitle, newLink, linkType, domainName




        # print(sourceData)
        # soup2 =BeautifulSoup(sourceData)
        # print(soup2)
        # imgURL2 = soup2.find("meta", property="og:image")

    except:
        print("2nd TRY didn't work!")


    imgURL = "generic"

    if caller == "webform":
        linkTitle = "{domainName}".format(domainName=domainName)
    else:
        linkTitle = "generic"

    linkType = "Website"
    return imgURL, linkTitle, newLink, linkType, domainName


            # try:
            #     print("pre respose ??")
            #     response = urllib.request.urlopen(req) ## urlopen(request)
            #     # print(response.read().decode('utf-8'))
            #     print("this worked??")
            #     sourceData = response.read().decode('utf-8')
            #
            # except urllib.error.HTTPError as e:
            #     print(e.code)
            #     print("do we get to error??")
