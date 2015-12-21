#!/usr/bin/env python3.4

HOST = ''

import socket
import sys
import fs,os
#TODO replace with threading module
from _thread import *
import subprocess

import settings

def resp(conn):
    conn.send(b'Lir Server Connection\nSend a command!\n')
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Receiving from client
        #TODO replace with buffer to receive large commands
        data = conn.recv(1024)
        data = str(data)[2:-1]
        #cleanup telnet or other methods of input
        if data.endswith("\\r\\n"):
            data = data[:-4]
        #android adds newline
        if data.endswith("\\n"):
            data = data[:-2]
        print("RECEIVED:",data)
        reply = b'OK;'
        try:
            mode,data = data.split(":",1)
        except:
            mode = "speech"
            
        if mode == "speech":
            command = subprocess.getoutput(fs.home()+"/.lir/dictionary \""+data+"\" "+fs.home()+"/.lir/actions/default.dic")
        elif mode == "direct":
            command = data
        else:
            reply += b"UnknownMode;"
        
        d = os.getcwd()
        os.chdir(fs.home()+"/.lir/bin")
        print("EXECUTING:",command)
        out = subprocess.getoutput("./"+command)+";"
        reply += out.encode('utf-8')
        os.chdir(d)
        
        if not data: 
            break
     
        try:
            conn.sendall(reply + b"\n")
        except:
            #client disconnected immediatly after submitting command
            pass
     
    #came out of loop
    conn.close()

def main():

    info = settings.ini(fs.home()+"/.lir/main.ini")
    PORT = int(info.get("server","port"))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Created Socket")
    
    try:
        s.bind((HOST,PORT))
    except socket.error as e:
        print ("Bind Failed.",e)
        return False
        
    print ("Bind Complete.")
    
    s.listen(10)
    print ("Socket Listening on port " + str(PORT))
    
    listen = True
    while listen:
        con,addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        start_new_thread(resp ,(con,))
    
if __name__ == "__main__":
    main()
