#!/usr/bin/env python3.4

import os
import subprocess as sp

import fs

PYTHON = "python3.4"

SERVER      = os.getcwd()+"/"+"server"
PAIR        = os.getcwd()+"/"+"pair"
WIZARD      = os.getcwd()+"/"+"wizard"
SETTINGS    = None

LIR_FOLDER  = fs.home() + "/.lir/"
FIRST_RUN = LIR_FOLDER + ".firstrun"

def attemptStart(cmd,pid,python = True):
    if os.path.exists(pid):
        with open(pid) as f:
            p = f.read().replace("\n","")
        if python:
            rpid = getPid(PYTHON,cmd)[0]
            if rpid != None:
                if rpid == p:
                    #already running
                    return 1
                else:
                    #different running
                    return 2
            else:
                os.system(cmd+" > /dev/null &")
                if python:
                    npid = getPid(PYTHON,cmd)
                    with open(pid,'w') as f:
                        f.write(npid[0])
                    return True
        else:
            #TODO implement later, not yet needed
            pass
    else:
        os.system(cmd+" > /dev/null &")
        if python:
            npid = getPid(PYTHON,cmd)
            with open(pid,'w') as f:
                f.write(npid[0])
            return True

def getPid(cmd,options):
    out = sp.getoutput("ps -Ao pid,cmd | grep "+options)
    out = out.split("\n")
    for i in range(0,len(out)):
        out[i] = out[i].split(" ")
        if len(out[i]) == 4:
            out[i] = out[i][1:]
    for o in out:
        if o[1] == cmd:
            return o
    return None

def main():
    if os.path.exists(LIR_FOLDER):
        if os.path.exists(FIRST_RUN):
            #TODO start notification service
            #start server
            server = attemptStart(SERVER,LIR_FOLDER+"/.server.pid")
            if server == 1:
                print("Server already running! PID:",getPid(PYTHON,SERVER)[0])
            elif server == 2:
                print("Server appears to be running! PID:",getPid(PYTHON,SERVER)[0])
            elif server == True:
                print("Server started! PID:",getPid(PYTHON,SERVER)[0])
        else:
            #start wizard
            wizard = attemptStart(WIZARD,LIR_FOLDER+"/.wizard.pid")
            if wizard == True:
                with open(FIRST_RUN,'w') as f:
                    f.write(":)")
            else:
                print("Failed to start wizard:",wizard)
    return 0

if __name__ == '__main__':
    main()
