#!/usr/bin/env python3.4

import fs,os
import settings
import tarfile
import lang

def add_dictionary(path,name):
    info = settings.ini(fs.expand_path("~/.lir/main.ini"))
    path = fs.expand_path(path)
    mode = path.split("/")[-1]
    fs.create("~/.lir/actions/"+mode+".dic")
    with open(fs.expand_path("~/.lir/actions/"+mode+".dic"),'a') as f:
        f.write("\n####\n#  "+name+"\n####\n")
        with open(path+"/"+info.get("general","language")+".dic") as src:
            f.write(src.read())
        

def installCompressed(path):
    #resolve path and open tar
    path = fs.expand_path(path)
    tar = tarfile.open(path,'r:gz')
    fs.create_directory("/tmp/lir")
    #extract into /tmp
    print(lang.get("install","extract"),path,"/tmp/lir")
    tar.extractall("/tmp/lir/")
    #load info
    info = settings.ini("/tmp/lir/info.ini")
    print(lang.get("install","start"),info.get("info","name"))
    #move files to "install" plugin
    fs.copy("/tmp/lir/info.ini","~/.lir/plugins/"+info.get("info","name").replace(" ","_").lower()+".ini")
    for s in ["tts","sst","services","bin"]:
        if info.has_section(s):
            if not fs.copy("/tmp/lir/"+s,"~/.lir/"+s):
                print(lang.get("error","transfer"),fs.expand_path("/tmp/lir/"+s),fs.expand_path("~/.lir/"+s))
                return False
    for dic in os.listdir("/tmp/lir/actions"):
        if os.path.isdir("/tmp/lir/actions/"+dic):
            add_dictionary("/tmp/lir/actions/"+dic,info.get("info","name"))
    fs.delete("/tmp/lir")
    print(lang.get("install","done"),info.get("info","name"))
    return True
    
def installFolder(path):
    path = fs.expand_path(path)
    info = settings.ini(path+"/info.ini")
    print(lang.get("install","start"),info.get("info","name"))
    #move files to "install" plugin
    fs.copy(path+"/info.ini","~/.lir/plugins/"+info.get("info","name").replace(" ","_").lower()+".ini")
    for s in ["tts","sst","services","bin"]:
        #if info.has_section(s):
        if os.path.exists(path+"/"+s):
            if not fs.copy(path+"/"+s,"~/.lir/"+s):
                print(lang.get("error","transfer"),fs.expand_path(path+"/"+s),fs.expand_path("~/.lir/"+s))
                return False
    if os.path.isdir(path+"/actions"):
        for dic in os.listdir(path+"/actions"):
            if os.path.isdir(path+"/actions/"+dic):
                add_dictionary(path+"/actions/"+dic,info.get("info","name"))
    print(lang.get("install","done"),info.get("info","name"))
    return True

def main():
    pass
    
if __name__ == "__main__":
    main()
