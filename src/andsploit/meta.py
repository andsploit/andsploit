from urllib2 import HTTPError, URLError, urlopen
from xml.etree import ElementTree

class Version:
    
    def __init__(self, version, date):
        major, minor, patch = version.split(".")
        
        self.date = date
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
    
    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch
    
    def __gt__(self, other):
        return self.major > other.major or \
            self.major == other.major and self.minor > other.minor or \
            self.major == other.major and self.minor == other.minor and self.patch > other.patch
    
    def __lt__(self, other):
        return self.major < other.major or \
            self.major == other.major and self.minor < other.minor or \
            self.major == other.major and self.minor == other.minor and self.patch < other.patch
    
    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.patch)


name = "andsploit"
vendor = ""
version = "v1.0"

contact = "andsploit@gmail.com"
description = "The Leading Android Security Testing Framework"
license = "BSD (3 clause)"
keywords = "andsploit android security framework"
url = "http://git.blue-lotus.net/hellok/bluexploit"

def print_version():
    print "%s %s\n" % (name, version)
    
def latest_version():
    try:
        xml = urlopen("https://git.blue-lotus.net/hellok/bluexploit/raw/master/dist/mainfest.xml").read()
        doc = ElementTree.fromstring(xml)
        
        return max(map(lambda n: Version(n.text[1:], n.attrib['release_date']), doc.findall('version')))
    except HTTPError:
        return None
    except URLError:
        return None

