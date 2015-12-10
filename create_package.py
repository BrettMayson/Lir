#!/usr/bin/env python3.4

import os
import settings
import fs
import tarfile

def main():
    print("Package Creator")
    print("Brett Mayson - 1.0 - Dec 2015")
    
    path = input("Path to plugin: ")
    
    #expand short file paths
    fs.expand_path(path)
        
    print("Path:",path)
        
    #get info from ini file
    if os.path.exists(path+"/info.ini"):
        l = settings.Settings(path+"/info.ini")
        print(l.get("info","name"))
    else:
        print("No Info.ini")
        return
    
    tar = tarfile.open(l.get("info","name").lower()+".tar.gz","w:gz")
    
    os.chdir(path)
    
    tar.add("info.ini")
    
    #check for tts modules
    if l.has_section("tts"):
        tar.add("tts")
        
    #check for stt modules
    if l.has_section("stt"):
        tar.add("stt")
        
    #check for services
    if l.has_section("services"):
        tar.add("services")
    
    if os.path.exists("bin"):
        tar.add("bin")
        
    if os.path.exists("actions"):
        tar.add("actions")
    
    tar.close()
    
if __name__ == "__main__":
    main()
