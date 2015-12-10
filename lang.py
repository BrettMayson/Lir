#!/usr/bin/env python3.4

import settings,os

#this will be replaced by language detection
if os.path.exists(os.getcwd()+"/langs/en.ini"):
    l = settings.ini("langs/en")
else:
    l = settings.ini("~/.lispeak/langs/en")
        
def get(section,key):
	return l.get(section,key)
