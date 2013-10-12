import httplib
import StringIO
import urllib2

from andsploit.configuration import Configuration

class Remote(object):
    """
    Remote is a wrapper around a set of andsploit remote repositories, and provides
    methods for managing them.
    
    A Remote can be instantiated to provide API access to the repository, to
    get information about available modules and download their source.
    """
    
    def __init__(self, url):
        self.url = url.endswith("/") and url or url + "/"
        
    @classmethod
    def all(cls):
        """
        Returns all known andsploit remotes.
        
        If the [remotes] section does not exist in the configuration file, we
        create it and add a default repository.
        """
        
        if not Configuration.has_section('remotes'):
            cls.create("https://raw.github.com/mwrlabs/andsploit-modules/repository/")
            
        return Configuration.get_all_values('remotes')
        
    @classmethod
    def create(cls, url):
        """
        Create a new andsploit remote, with the specified URL.
        
        If the URL already exists, no remote will be created.
        """
        
        if cls.get(url) == None:
            Configuration.set('remotes', url, url)
            
            return True
        else:
            return False
    
    @classmethod
    def delete(cls, url):
        """
        Removes a andsploit remote, with the specified URL.
        """
        
        if cls.get(url) != None:
            Configuration.delete('remotes', url)
            
            return True
        else:
            raise UnknownRemote(url)
    
    @classmethod
    def get(cls, url):
        """
        Get an instance of Remote, initialised with the remote settings.
        """
        
        url = Configuration.get('remotes', url)
        
        if url != None:
            return cls(url)
        else:
            return None
    
    def buildPath(self, path):
        """
        Build a full URL for a given path on this remote.
        """
        
        return self.url + str(path)
    
    def download(self, module):
        """
        Download a module from the remote, if it exists.
        """
        
        try:
            return self.getPath(module)
        except urllib2.HTTPError:
            # such as not found: there is no module to download
            return None
        except urllib2.URLError:
            # such as connection refused: the server simply isn't there
            return None
    
    def getPath(self, path):
        """
        Fetch a file from the remote.
        """
        
        r = urllib2.urlopen(self.buildPath(path))
        socket = FakeSocket(r.read())
        r.close()
        
        response = httplib.HTTPResponse(socket)
        response.begin()
        data = response.read()
        response.close()
        
        return data
            
        
class FakeSocket(StringIO.StringIO):
    """
    FakeSocket is used to interface between urllib2 and httplib, which aren't
    totally compatible.
    """
    
    def makefile(self, *args, **kwargs):
        return self
    
class UnknownRemote(Exception):
    """
    Raised if a Remote is specified that isn't in the configuration.
    """
    
    def __init__(self, url):
        Exception.__init__(self)
        
        self.url = url
    
    def __str__(self):
        return "The remote %s is not registered." % self.url
    