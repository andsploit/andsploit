import fnmatch
import glob
import os
import setuptools

from andsploit import meta

def find_files(src):
    matches = []
    
    for root, dirnames, filenames in os.walk(src):
        matches.extend(map(lambda f: os.path.join(root, f), filenames))
    
    return matches

def find_libs(src):
    matches = []
    
    for root, dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(dirnames, 'lib'):
            tmp=glob.glob(os.path.join(root, filename, "*", "*"))
            print tmp
            #matches.extend(tmp)
        for filename in fnmatch.filter(dirnames, 'libs'):
            tmp=glob.glob(os.path.join(root, filename, "*", "*"))
            print tmp
            for i in tmp:
                if os.path.isdir(i):
                    tmp.remove(i)
            matches.extend(tmp)
    return map(lambda fn: os.path.basename(fn), matches)

#['src/andsploit/lib/weasel/armeabi']
#['src/andsploit/modules/tools/setup/minimal-su/libs/armeabi1/__init__.py', 'src/andsploit/modules/tools/setup/minimal-su/libs/armeabi1/su']
#find_libs("src")
    
setuptools.setup(
  name = meta.name,
  version = meta.version,
  author = meta.vendor,
  author_email = meta.contact,
  description = meta.description,
  long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
  license = meta.license,
  keywords = meta.keywords,
  url = meta.url,

  packages = setuptools.find_packages("src"),
  package_dir = {   "andsploit": "src/andsploit",
                    "mwr": "src/mwr",
                    "pydiesel": "src/pydiesel" },
  package_data = { "": ["*.apk", "*.bks", "*.crt", "*.docx", "*.jar", "*.key", "*.sh", "*.xml", "busybox"] + ['src/andsploit/lib/weasel/armeabi']+['src/andsploit/modules/tools/setup/minimal-su/libs/armeabi/__init__.py', 'src/andsploit/modules/tools/setup/minimal-su/libs/armeabi/su'],
                   "andsploit": ["lib/aapt",
                                 "lib/mac_aapt",
                              "lib/aapt.exe",
                              "lib/*.apk",
                              "lib/*.jar",
                              "lib/*.pem",
                              "lib/*.pk8",
                              "lib/weasel/*",
                              "server/web_root/*" ] },
  scripts = ["bin/andsploit", "bin/andsploit-complete"],
  install_requires = ["protobuf==2.4.1", "pyopenssl==0.13"],
  classifiers = [])
