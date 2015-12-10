#!/usr/bin/env python3.4

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0
    
import os

class ini():
    def __init__(self,name):
        # instantiate config
        self.config = ConfigParser()
        #file name
        self.name = name if name.endswith(".ini") else name+".ini"
        import fs
        self.name = fs.expand_path(self.name)

        # parse existing file
        if os.path.exists(self.name):
            self.config.read(self.name)

    def get(self,section,key):
        #get a value from the config
        return self.config.get(section,key)
        
    def set(self,section,key,value):
        #set a value in the config
        return self.config.set(section, key, value)

    def create_section(self,name):
        #create a new section in the config
        if not self.has_section(name):
            self.config.add_section(name)

    def has_section(self,name):
        #check for a section in the config
        return self.config.has_section(name)

    def save(self):
        import fs
        try:
            BACKUP = "/tmp/new_settings.ini"
            #save to an alternate file to assure no data loss
            with open(BACKUP, "w") as configfile:
                self.config.write(configfile)
            fs.delete(self.name)
            fs.move(BACKUP,self.name)
            return True
        except:
            fs.delete(BACKUP)
        #    return False
