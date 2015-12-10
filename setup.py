#!/usr/bin/env python3.4

import fs
import lang
import settings
import package_manager as pm

import os
import argparse

parser = argparse.ArgumentParser(description='Setup Lir')
parser.add_argument('--debug', type=bool, help='Display debug messages')
args = parser.parse_args()

if args.debug:
    DEBUG = True
else:
    DEBUG = False

def debug(*text):
    if DEBUG:
        print("[DEBUG]",text)

def main():
    print(lang.get("setup","welcome"))
    print(lang.get("setup","info"))
    print()
    print(lang.get("setup","notice"))
    print()
    #Create directories
    fs.delete("~/.lir")
    fs.create_directory("~/.lir")
    for d in ["plugins","tts","stt","actions","services","bin","langs"]:
        fs.create_directory("~/.lir/"+d)
    fs.create("~/.lir/actions/default.dic")
    fs.copy("langs","~/.lir/langs")
        
    #Create ini
    ini = settings.ini("~/.lir/main.ini")
    ini.create_section("general")
    try:
        import pwd,os
        name = pwd.getpwuid(os.getuid())[4].replace(",","")
        print()
        if input("Is "+name+" your name? [Y/N]").lower() == "y":
            ini.set("general","name",name)
        else:
            ini.set("general","name",input(lang.get("setup","name")))
    except:
        ini.set("general","name",input(lang.get("setup","name")))
        
    #make dictionary program
    debug(lang.get("setup","build"),"Dictionary")
    os.chdir("dictionary")
    fs.delete("dictionary")
    if DEBUG:
        os.system("make")
    else:
        fs.system("make")
    os.chdir("../")
    fs.copy("dictionary/dictionary","~/.lir/dictionary")
        
    #Install required packages
    
    #Install default plugins
    if not pm.installFolder("dev_plugins/espeak"):
        print(lang.get("error","install"),"espeak")
    else:
        ini.create_section("tts")
        #right now espeak is the default tts engine
        ini.set("tts","engine","espeak")
        print()
        #ask if tts should be used
        ini.set("tts","read-responses",str(input("Do you want Lir to read out responses? [Y/N]").lower() == "y"))
        print()
        
    if not pm.installFolder("dev_plugins/pico-tts"):
        print(lang.get("error","install"),"pico-tts")
    #else:
    #    ini.create_section("tts")
    #    ini.set("tts","engine","pico")
        
    if not pm.installFolder("dev_plugins/google-tts"):
        print(lang.get("error","install"),"google-tts")
    #else:
    #    ini.create_section("tts")
    #    ini.set("tts","engine","google-tts")
        
    if not pm.installFolder("dev_plugins/say"):
        print(lang.get("error","install"),"say")
        
    if not pm.installFolder("dev_plugins/notify"):
        print(lang.get("error","install"),"notify")
        
    if not pm.installFolder("dev_plugins/media-control"):
        print(lang.get("error","install"),"media-control")
        
    #copy needed python scripts
    for f in ["settings.py","lang.py","fs.py","lir.py"]:
        fs.copy(f,"~/.lir/bin")
        fs.copy(f,"~/.lir/services")
        fs.copy(f,"~/.lir/tts")
        
    #Create server info in config
    ini.create_section("server")
    ini.set("server","host","127.0.0.1")
    ini.set("server","port","8090")
        
    debug("Saving ini")
    ini.save()
    print()
    print(lang.get("setup","done"))
    
if __name__ == "__main__":
    main()
