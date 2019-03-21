"""
This module is use to collect data from google search result
"""
__all__ = ["google_search", "google_docs_download", "google_docs_search"]

# import default system library
import random
import os
from time import sleep
import certifi
# import 3rd party library
from google import google as googlesearchapi
import pycurl

# import shared library
from base0.constant import OFFICEFILENAME

def google_search(keyword, pages=1):
    """ return search result """
    searchresults = googlesearchapi.search(keyword, pages)
    return searchresults

def google_docs_download(searchresults, ext, path=None, wait=True):
    """ download google documents"""
    filelist = []
    if path is None:
        currentpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(currentpath, "googledoc")
        os.makedirs(path)
    for searchresult in searchresults:
        filename = searchresult.name.split(ext)[0]
        if filename[-1] != ".":
            filename = f"{filename}.{ext}"
        else:
            filename = f"{filename}{ext}"
        file_ = os.path.join(path, filename)
        print(file_)
        print("*"*8)        
        print(searchresult.name)
        print("*"*8)
        print(searchresult.description)        
        try:
            with open(file_, "wb") as filehandle:
                content = pycurl.Curl()
                content.setopt(content.URL, searchresult.link)   
                content.setopt(content.FOLLOWLOCATION, True)             
                content.setopt(content.CAINFO, certifi.where())
                content.setopt(content.WRITEDATA, filehandle)
                content.perform()
                filelist.append(file_)
                if wait:
                    sleep(int(random.random()*10))
        except OSError as error:
            print(error,file_)

def google_docs_search(keyword, pages=1, ext=None, download=True):
    """ get document from google doc based on keyword """
    if ext is None:
        ext = random.choice(OFFICEFILENAME)
    searchresults = google_search(f"{keyword} {ext} site:docs.google.com", pages)
    if download:
        if isinstance(download, str):
            google_docs_download(searchresults, ext, path=download)
        else:
            google_docs_download(searchresults, ext)
    return searchresults


def main():
    """ main function for local usage"""
    pass

if __name__ == '__main__':
    main()
