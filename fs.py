#!/usr/bin/env python3.4

import os
import shutil
import subprocess

DEBUG = False

def debug(*text):
    if DEBUG:
        print("[DEBUG]",text)
        
def system(cmd):
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(cmd, stdout=devnull, stderr=subprocess.STDOUT)

def expand_path(path):
    #expand home directory
    path = os.path.expanduser(path)
    if not path.startswith("/"):
        path = os.getcwd() + "/" + path
    #resolve relative paths
    path = os.path.realpath(path)
    return path

def move(src,dst):
    import lang
    src = expand_path(src)
    dst = expand_path(dst)
    shutil.move(src,dst)
    debug(lang.get("files","move"),src,dst)
    return True

def copy(src,dst):
    import lang
    src = expand_path(src)
    dst = expand_path(dst)
    try:
        os.makedirs(dst)
    except:
        pass
    if os.path.isdir(src):
        files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        dirs =  [f for f in os.listdir(src) if os.path.isdir(os.path.join(src, f))]
        
        for f in files:
            if not f.endswith("~"):
                shutil.copy(os.path.join(src,f),os.path.join(dst,f))
                debug(lang.get("files","copy"),os.path.join(src,f),os.path.join(dst,f))
            
        for d in dirs:
            if copy(os.path.join(src,f),os.path.join(dst,f)) == False:
                return False
        return True
    elif os.path.isfile(src):
        shutil.copy(src,dst)
        debug(lang.get("files","copy"),src,dst)
        return True
    else:
        return False

def delete(path):
    import lang
    path = expand_path(path)
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            debug(lang.get("files","delete_dir"),path)
            return True
        elif os.path.isfile(path):
            os.remove(path)
            debug(lang.get("files","delete_file"),path)
            return True
        else:
            return False
    else:
        return False
        
def create(path):
    path = expand_path(path)
    if not os.path.exists(path):
        open(path, 'a').close()
        
def create_directory(directory):
    import lang
    directory = expand_path(directory)
    if not os.path.exists(directory):
        debug(lang.get("files","create_dir"),directory)
        os.makedirs(directory)

def home():
    return expand_path("~")
