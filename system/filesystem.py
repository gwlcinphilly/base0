"""
This module include basic file systme operation
"""
__all__ = []

import os
import hashlib

def listfiles(path):
    files = []
    fileslist = []
    folderlist = []
    for root, dirs, files in os.walk(path,topdown=False):
        for name in files:
            files.append(name)
            filename = os.path.join(root,name)
            fileslist.append(filename)            
            if root not in folderlist:
                folderlist.append(root)
    return files, fileslist, folderlist

def folderend(folder, win=True):
    """add forward and backwrd slash to folder name"""
    if folder != "":
        if folder[-1] != "\\" and folder[-1] != "/":
            if win:
                folder = folder+"\\"
            else:
                folder = folder+"/"
    return folder

def fileinfo(filename,level=0):
    """ return basic file information based on the level
        level 0    : basic file name, size 
        level 10   : include file hash
    """
    fileinfo = {}
    infomaps = {"size" : "st_size",
                'createtime' : 'st_ctime',
                'modifytime' : 'st_mtime'}
    level0list = ['size', 'createtime','modifytime']
    level10list = ['lines', 'hash']
    fileinfo['name'] = filename
    fileinfo['file'] = os.path.basename(filename) 
    fileinfo['path'] = os.path.dirname(filename)
    for entry in level0list:
        fileinfo[entry] = getattr(os.stat(filename), infomaps[entry])

    if level >10:
        for entry in level10list:
            blocksize = 1024
            with open(filename,'rb') as filehandle:
                if entry == "lines":
                    lines = 0 
                    buf = filehandle.raw.read(blocksize) 
                    while buf:
                        lines +=buf.count(b'\n')
                        buf = filehandle.raw.read(blocksize)
                    fileinfo['lines'] = lines
                elif entry == "hash":
                    hasher = hashlib.md5()
                    buf= filehandle.read(blocksize)
                    while len(buf) >0:
                        hasher.update(buf)
                        buf = filehandle.read(blocksize)
                    fileinfo['hash'] = hasher.hexdigest()
    
    return fileinfo
    